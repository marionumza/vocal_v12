# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from datetime import datetime, timedelta
from lxml import etree
from openerp.osv.orm import setup_modifiers
import openerp.addons.decimal_precision as dp
import decimal

import logging
_logger = logging.getLogger(__name__)

MP_MEMBERSHIP_STATE = [
    ('draft', 'Draft Member'),              #If active seller membership is in draft state
    ('canceled', 'Cancelled Member'),       #If active seller membership is in canceled state
    ('old', 'Expire Member'),               #If active seller membership is in old state
    ('pending', 'Pending Member'),          #If active seller membership is in pending state
    ('paid', 'Paid Member'),                #If active seller membership is in paid state
    ('free', 'Free Member'),                #If seller is a free member
]

class ResPartner(models.Model):
    _inherit = 'res.partner'

    mp_membership_plan_ids = fields.One2many('seller.membership', 'partner_id', string='MP Membership')
    free_membership = fields.Boolean(string='Free Member', help="Select if you want to give free membership.")
    mp_membership_amount = fields.Float(string='Membership Amount', digits=(16, 2), help='The price negotiated by the partner')
    mp_membership_state = fields.Selection(MP_MEMBERSHIP_STATE, compute='_compute_mp_membership_state', string='MP Membership Status', help="It indicates the membership status.\n"
             "-Draft Member: When membership has no invoice.\n"
             "-Pending Member: A member who has purchased/applied for the marketplace membership and whose invoice is going to be created or not paid yet.\n"
             "-Paid Member: A member who has paid the marketplace membership amount.\n"
             "-Expired Member: A member whose marketplace membership date has expired.\n"
             "-Cancelled Member: A member who has cancelled his marketplace membership.\n")
    mp_membership_start_date = fields.Date(compute='_compute_mp_membership_start_stop', string='Valid From', help="Date from which membership becomes active.", store=True)
    mp_membership_stop_date = fields.Date(compute='_compute_mp_membership_start_stop', string='Expire On', help="Date until which membership remains active.", store=True)
    membership_cancel_date = fields.Date(compute='_compute_mp_membership_start_stop', string='Cancel Date', help="Date on which membership has been cancelled", store=True)
    no_of_product = fields.Integer("# of Allow Products")

    @api.onchange("free_membership")
    def onchange_free_membership(self):
        if self.free_membership:
            config_setting_obj = self.env['res.config.settings'].sudo().get_values()
            self.no_of_product = config_setting_obj.get("mp_membership_product", 0)
        else:
            self.no_of_product = 0

    @api.depends('mp_membership_plan_ids', 'mp_membership_plan_ids.account_invoice_line_id.invoice_id.state',
                 'mp_membership_plan_ids.account_invoice_line_id.invoice_id.invoice_line_ids',
                 'mp_membership_plan_ids.account_invoice_line_id.invoice_id.payment_ids',
                 'free_membership', 'mp_membership_plan_ids.mp_membership_plan_id.product_tmpl_id.no_of_product', 'mp_membership_plan_ids.state', 'mp_membership_plan_ids.mp_membership_date_from', 'mp_membership_plan_ids.mp_membership_date_to',
                 'mp_membership_plan_ids.mp_membership_cancel_date')
    def _compute_mp_membership_start_stop(self):
        for partner in self:
            x =  self.env['seller.membership'].sudo().search([('partner_id', '=', partner.id), ('mp_membership_cancel_date','=',False), ('is_active','=',True)], limit=1)
            if x:
                partner.mp_membership_start_date = x.mp_membership_date_from
                partner.mp_membership_stop_date = x.mp_membership_date_to

            y = self.env['seller.membership'].sudo().search([('partner_id', '=', partner.id), ('is_active','=',True)], limit=1, order='mp_membership_cancel_date')
            if y:
                partner.membership_cancel_date = y.mp_membership_cancel_date

    @api.depends('mp_membership_plan_ids', 'mp_membership_plan_ids.account_invoice_line_id.invoice_id.state',
                'mp_membership_plan_ids.account_invoice_line_id.invoice_id.invoice_line_ids',
                'mp_membership_plan_ids.account_invoice_line_id.invoice_id.payment_ids',
                'free_membership',
                'mp_membership_plan_ids.mp_membership_date_from', 'mp_membership_plan_ids.mp_membership_date_to')
    def _compute_mp_membership_state(self):
        for partner in self:
            if partner.free_membership:
                partner.mp_membership_state = "free"
            else:
                seller_membership_obj = self.env['seller.membership'].sudo().search([
                    ('partner_id', '=', partner.id), ('is_active','=',True)
                ], limit=1)
                if seller_membership_obj:
                    partner.mp_membership_state = seller_membership_obj.state
                    if seller_membership_obj.state == "paid":
                        partner.write({"no_of_product": seller_membership_obj.no_of_product})
                        # partner.no_of_product = seller_membership_obj.no_of_product
                    else:
                        partner.write({"no_of_product": 0})
                        # partner.no_of_product = 0
                else:
                    seller_membership_obj2 = self.env['seller.membership'].sudo().search([('partner_id', '=', partner.id)], limit=1, order='mp_membership_date_to desc')
                    if seller_membership_obj2:
                        partner.mp_membership_state = seller_membership_obj2.state
                        if seller_membership_obj2.state == "paid":
                            partner.write({"no_of_product": seller_membership_obj2.no_of_product})
                            # partner.no_of_product = seller_membership_obj.no_of_product
                        else:
                            partner.write({"no_of_product": 0})
                            # partner.no_of_product = 0

    @api.multi
    def cancel_seller_mp_membership(self):
        for rec in self:
            rec.sudo().mp_membership_plan_ids.membership_action_cancel()

    @api.multi
    def create_mp_membership_invoice(self, product_id=None, datas=None):
        """ Create Seller Invoice of Membership for partners.
        @param datas: datas has dictionary value which consist Id of Membership product and Cost Amount of Membership.
                      datas = {'membership_product_id': None, 'amount': None}
        """
        product_id = product_id or datas.get('membership_product_id')
        amount = datas.get('amount', 0.0)
        invoice_list = []
        for partner in self:
            addr = partner.address_get(['invoice'])
            if partner.free_membership:
                raise UserError(_("Partner is a free Member."))
            if not addr.get('invoice', False):
                raise UserError(_("Partner doesn't have an address to make the invoice."))
            invoice = self.env['account.invoice'].create({
                'partner_id': partner.id,
                'account_id': partner.property_account_receivable_id.id,
                'fiscal_position_id': partner.property_account_position_id.id
            })
            line_values = {
                'product_id': product_id,
                'price_unit': amount,
                'invoice_id': invoice.id,
            }
            # create a record in cache, apply onchange then revert back to a dictionnary
            invoice_line = self.env['account.invoice.line'].new(line_values)
            invoice_line._onchange_product_id()
            line_values = invoice_line._convert_to_write({name: invoice_line[name] for name in invoice_line._cache})
            line_values['price_unit'] = amount
            invoice.write({'invoice_line_ids': [(0, 0, line_values)]})
            invoice_list.append(invoice.id)
            invoice.compute_taxes()
        return invoice_list

    @api.multi
    def get_seller_global_settings(self, config_setting_obj):
        self.ensure_one()
        result = super(ResPartner, self).get_seller_global_settings(config_setting_obj)
        if self.free_membership:
            result.update({
                'no_of_product' : config_setting_obj.get("mp_membership_product"),
            })
        return result

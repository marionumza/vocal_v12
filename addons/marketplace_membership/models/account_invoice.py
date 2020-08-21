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

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_invoice_paid(self):
        res = super(AccountInvoice, self).action_invoice_paid()
        for rec in self:
            if rec.state == "paid":
                mp_membership_obj = self.env["seller.membership"].sudo().search([('account_invoice_id', '=', rec.id)])
                for mp_member in mp_membership_obj:
                    mp_member.disable_all_make_active_membership()
                    mp_membership_plan_dates = mp_member.mp_membership_plan_id.product_tmpl_id.get_mp_membership_plan_date_range()
                    if mp_membership_plan_dates:
                        mp_member.date_from = mp_membership_plan_dates.get("date_from", False)
                        mp_member.date_to = mp_membership_plan_dates.get("date_to", False)
        return res

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.model
    def create(self, vals):
        invoice_line_obj = super(AccountInvoiceLine, self).create(vals)
        mp_membership_obj = self.env['seller.membership'].sudo()
        if invoice_line_obj.invoice_id.type == 'out_invoice' and invoice_line_obj.product_id.wk_mp_membership and not mp_membership_obj.search([('account_invoice_line_id', '=', invoice_line_obj.id)]):
            # Product in line is a marketplace membership product
            mp_membership_plan_dates = invoice_line_obj.product_id.product_tmpl_id.get_mp_membership_plan_date_range()
            date_from = mp_membership_plan_dates.get("date_from", False)
            date_to = mp_membership_plan_dates.get("date_to", False)
            if invoice_line_obj.invoice_id.date_invoice and invoice_line_obj.invoice_id.date_invoice > date_from and invoice_line_obj.invoice_id.date_invoice < date_to:
                mp_membership_plan_dates = invoice_line_obj.product_id.product_tmpl_id.get_mp_membership_plan_date_range(date=invoice_line_obj.invoice_id.date_invoice)
                date_from = mp_membership_plan_dates.get("date_from", False)
                date_to = mp_membership_plan_dates.get("date_to", False)
                # date_from = invoice_line_obj.invoice_id.date_invoice
            mp_membership_obj.sudo().create({
                'partner_id': invoice_line_obj.invoice_id.partner_id.id,
                'mp_membership_plan_id': invoice_line_obj.product_id.id,
                'mp_membership_fee': invoice_line_obj.price_unit,
                'date': fields.Date.today(),
                'mp_membership_date_from': date_from,
                'mp_membership_date_to': date_to,
                'account_invoice_line_id': invoice_line_obj.id,
                'no_of_product': invoice_line_obj.product_id.no_of_product,
                'order_line_id': invoice_line_obj.sale_line_ids.ids[0] if invoice_line_obj.sale_line_ids else False
            })
            #Untick seller from Free member
            invoice_line_obj.invoice_id.partner_id.free_membership = False
            invoice_line_obj.invoice_id.message_partner_ids = [(4, invoice_line_obj.invoice_id.partner_id.id)]
        return invoice_line_obj

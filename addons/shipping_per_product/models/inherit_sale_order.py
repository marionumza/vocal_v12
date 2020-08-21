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
from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _check_carrier_quotation(self, force_carrier_id=None):
        self._remove_delivery_line()
        self.write({'carrier_id': False, 'delivery_price': 0.0})
        self.order_line.filtered('is_delivered').write({
            'delivery_carrier_id' : False,
            'delivery_charge' : 0.0,
            'is_delivered': False
        })
        return True

    def _compute_amount_total_without_delivery(self):
        self.ensure_one()
        line = self.order_line.filtered('active')
        if len(line) == 1 and line.is_delivered:
            return line.price_subtotal + line.price_tax
        else:
            return super(SaleOrder, self)._compute_amount_total_without_delivery()

    def set_sol_delivery_charge(self, sol):
        order_line_id = self.env["sale.order.line"].browse(int(sol))
        inactive_sol = self.order_line.filtered(lambda l: l.id != order_line_id.id)
        inactive_sol.write({'active':False})

        order = self.browse(self.id)
        order.delivery_rating_success = False
        order_line_id.write({
            'is_delivered': True
        })
        res = order.carrier_id.rate_shipment(order)

        order_line_id.write({
            'delivery_carrier_id': order.carrier_id.id,
            'delivery_charge': res["price"],
            'est_delivery_days': res.get('est_delivery_days', False),
            'is_delivered': True
        })

        inactive_sol.write({'active':True})
        return res

    def get_delivery_price(self, sol=None):
        for order in self.filtered(lambda o: o.state in ('draft', 'sent') and len(o.order_line) > 0):
            res = {}
            # For website when sol carrier selected
            # if sol and sol.id in order.order_line.ids:
            if sol:
                res = order.set_sol_delivery_charge(sol)
                price_unit = order.get_total_sol_delivery_price()
                order.write({'delivery_price':price_unit})

            # For backend when sol carrier selected
            elif order.carrier_id.is_sol_carrier:
                carrier_id = order.carrier_id
                order.delivery_price = 0.0
                for line in order.order_line.filtered(lambda l: l.is_delivery == False):
                    if line.delivery_carrier_id:
                        order.write({'carrier_id' : line.delivery_carrier_id.id})
                        res = order.set_sol_delivery_charge(line.id)
                    else:
                        line.delivery_charge = 0.0
                price_unit = order.get_total_sol_delivery_price()
                order.write({'carrier_id': carrier_id.id, 'delivery_price':price_unit})

            # For backend when normal carrier is selected
            else:
                super(SaleOrder,order).get_delivery_price()

            if res:
                if res['success']:
                    order.delivery_rating_success = True
                    order.delivery_message = res['warning_message']
                else:
                    order.delivery_rating_success = False
                    order.delivery_price = 0.0
                    order.delivery_message = res['error_message']


    def _check_carrier_sol_quotation(self, sol=None, force_carrier_id=None):
        self.ensure_one()
        DeliveryCarrier = self.env['delivery.carrier']

        if self.only_services:
            self.write({'carrier_id': None})
            self._remove_delivery_line()
            return True
        else:
            # attempt to use partner's preferred carrier
            if not force_carrier_id and self.partner_shipping_id.property_delivery_carrier_id:
                force_carrier_id = self.partner_shipping_id.property_delivery_carrier_id.id

            carrier = force_carrier_id and DeliveryCarrier.browse(force_carrier_id) or self.carrier_id
            # available_carriers = self._get_delivery_methods()
            # if carrier:
            #     if carrier not in available_carriers:
            #         carrier = DeliveryCarrier
            #     else:
            #         available_carriers -= carrier
            #         available_carriers = carrier + available_carriers
            # if force_carrier_id or not carrier or carrier not in available_carriers:
            #     for delivery in available_carriers:
            #         verified_carrier = delivery._match_address(self.partner_shipping_id)
            #         if verified_carrier:
            #             carrier = delivery
            #             break
            if carrier:
                self.write({'carrier_id': carrier.id})
                self.get_delivery_price(sol)
                self.set_dynamic_delivery_line()

        return bool(carrier)

    def get_total_sol_delivery_price(self):
        amount = sum(self.order_line.filtered('is_delivered').mapped('delivery_charge'))
        return amount


    @api.multi
    def set_dynamic_delivery_line(self):
        self._remove_delivery_line()

        carrier_id = self.env["delivery.carrier"].search([('is_sol_carrier','=',True)],limit=1)

        for order in self:
            if order.state not in ('draft', 'sent'):
                raise UserError(_('You can add delivery price only on unconfirmed quotations.'))
            # elif not order.delivery_rating_success:
            #     raise UserError(_('Please use "Check price" in order to compute a shipping price for this quotation.'))
            else:
                price_unit = order.get_total_sol_delivery_price()
                delivery_lines = order.order_line.filtered('is_delivery')
                delivery_line = delivery_lines[0] if len(delivery_lines) > 0 else False
                if delivery_line:
                    delivery_line.write({'price_unit':price_unit})
                else:
                    order._create_delivery_line(carrier_id, price_unit)
            if carrier_id:
                order.write({'carrier_id':carrier_id.id})
        return True

    @api.multi
    def set_delivery_per_sol(self):
        context = dict(self._context) or {}

        for rec in self:
            context['active_id'] = rec.id

            if rec.carrier_id.is_sol_carrier:
                return {
                    'name':'Delivery Method Per Product',
                    'type':'ir.actions.act_window',
                    'res_model':'sol.delivery.carrier',
                    'view_mode':'form',
                    'view_type':'form',
                    'view_id':self.env.ref('shipping_per_product.sol_delivery_carrier_wizard_form_view').id,
                    'context' : context,
                    'target':'new',
                }
            else:
                return self.get_delivery_price()

    @api.multi
    def set_sol_delivery_line(self):

        # Remove delivery products from the sales order
        self._remove_delivery_line()

        for order in self:
            if order.carrier_id.is_sol_carrier:
                order.set_dynamic_delivery_line()
            else:
                order.set_delivery_line()


class SaleOderLine(models.Model):
    _inherit = "sale.order.line"

    delivery_carrier_id = fields.Many2one("delivery.carrier", string="Delivery Method")
    est_delivery_days = fields.Char("Delivery days for selected service", copy=False)
    delivery_charge = fields.Float("Delivery Price", readonly=True, copy=False)
    is_delivered = fields.Boolean("Delivered")
    active = fields.Boolean("Active", default=True)

    @api.one
    def get_delivery_carrier_ids(self):
        address = self.order_id.partner_shipping_id
        delivery_carriers = self.product_id.product_tmpl_id.delivery_carrier_ids.filtered('website_published')
        data = delivery_carriers.available_carriers(address)
        data = data if len(data) > 0 else False
        return data

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

class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    product_temp_ids = fields.Many2many("product.template", "product_delivery_carriers", "delivery_carrier_ids", "product_temp_ids")
    is_sol_carrier = fields.Boolean("SOL Carrier")


    @api.multi
    def write(self, vals):
        for rec in self:
            if vals.get('website_published',False) and rec.is_sol_carrier:
                raise UserError(_('You can not publish the sale order line delivery carrier.'))
            if vals.get('active') != None and not vals.get('active') and rec.is_sol_carrier:
                raise UserError(_('You can not inactive the sale order line delivery carrier.'))
        return super(DeliveryCarrier, self).write(vals)

    @api.multi
    def unlink(self):
        if self.is_sol_carrier:
            raise UserError(_('You can not delete the sale order line delivery carrier.'))
        else:
            return super(WebsitePreorderConfigSettings, self).unlink()


class StockMove(models.Model):
    _inherit = 'stock.move'


    def _assign_picking(self):
        """ Create picking seperatly for each move """
        Picking = self.env['stock.picking']
        dynamic_carrier = self.env["delivery.carrier"].search([('is_sol_carrier','=',True)],limit=1)
        for move in self:
            if move.sale_line_id.order_id.carrier_id.id == dynamic_carrier.id:
                values = move._get_new_picking_values()
                values.update({
                    'carrier_id' : move.sale_line_id.delivery_carrier_id.id
                })
                picking = Picking.create(values)
                move.write({'picking_id': picking.id})
            else:
                super(StockMove,move)._assign_picking()
        return True

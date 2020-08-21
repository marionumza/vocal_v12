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
from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = 'stock.move'


    def _assign_picking(self):
        """ Create picking seperatly for each move """
        Picking = self.env['stock.picking']
        for move in self:
            if move.sale_line_id.order_id.carrier_id.is_sol_carrier:
                values = move._get_new_picking_values()
                values.update({
                    "carrier_id" : move.sale_line_id.delivery_carrier_id.id,
                    "marketplace_seller_id": move.product_id.marketplace_seller_id.id
                })
                picking = Picking.create(values)
                move.write({'picking_id': picking.id})
            else:
                super(StockMove,move)._assign_picking()
        return True

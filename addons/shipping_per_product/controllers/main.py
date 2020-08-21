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
from odoo import http, _
from odoo.http import request

import logging
_logger = logging.getLogger(__name__)

class ProductShipping(http.Controller):

    @http.route(['/shop/sol/update_carrier'], type='json', auth='public', methods=['POST'], website=True, csrf=False)
    def update_shop_sol_carrier(self, **post):
        order_line_id = request.env["sale.order.line"].browse(int(post['order_line']))
        order = order_line_id.sudo().order_id
        carrier_id = int(post['carrier_id'])
        if order_line_id and order.state == 'draft':
            order.sudo()._check_carrier_sol_quotation(sol=order_line_id.id,force_carrier_id=carrier_id)
            return {'status': order.delivery_rating_success,
                    'error_message': order.delivery_message,
                    'carrier_id': carrier_id,
                    'new_total_delivery_amount': order.amount_delivery,
                    'new_amount_delivery': order_line_id.sudo().delivery_charge,
                    'new_amount_untaxed': order.amount_untaxed,
                    'new_amount_tax': order.amount_tax,
                    'new_amount_total': order.amount_total}

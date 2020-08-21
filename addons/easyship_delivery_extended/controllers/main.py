# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from datetime import datetime


class WebsiteSale(WebsiteSale):

    @http.route(['/shop/sol/update_carrier'], type='json', auth='public', methods=['POST'], website=True, csrf=False)
    def update_shop_sol_carrier(self, **post):
        order_line_id = request.env["sale.order.line"].browse(int(post['order_line']))
        order = order_line_id.sudo().order_id
        carrier_id = int(post['carrier_id'])
        if order_line_id and order.state == 'draft':
            order.sudo()._check_carrier_sol_quotation(sol=order_line_id.id, force_carrier_id=carrier_id)
            results = {
                'status': order.delivery_rating_success,
                'error_message': order.delivery_message,
                'carrier_id': carrier_id,
                'est_delivery_days': order_line_id.sudo().est_delivery_days,
                'new_total_delivery_amount': order.amount_delivery,
                'new_amount_delivery': order_line_id.sudo().delivery_charge,
                'new_amount_untaxed': order.amount_untaxed,
                'new_amount_tax': order.amount_tax,
                'new_amount_total': order.amount_total}
            if carrier_id:
                results.update({'order_line_id': post.get('order_line_id', False)})
                carrier_id = request.env['delivery.carrier'].sudo().browse(int(carrier_id))
                if carrier_id.delivery_type == 'easyship_ts':
                    available_services = request.env['es.service.charge'].sudo().search([('order_id', '=', order.id), ('order_line_id', '=', order_line_id.id), ('courier_does_pickup', '=', True)],
                                                                                        limit=7)
                    results.update({'es_service_ids': [{
                        'id': eservice.id,
                        'service_name': eservice.courier_name,
                        'con_value': order.currency_id.symbol + str(
                            order.carrier_id.product_id.company_id.currency_id._convert(eservice.total_charge,
                                                                                        order.currency_id,
                                                                                        order.company_id,
                                                                                        datetime.today())),
                        'es_service_id': order.es_service_id and order.es_service_id.id or False,
                        'delivery_time': eservice.delivery_time,
                        'shipment_charge': eservice.shipment_charge,
                        'total_charge': eservice.total_charge,
                        'total_amount_format': order.currency_id.symbol + str(eservice.total_charge)} for eservice in
                        available_services]
                    })
            if carrier_id and not carrier_id.delivery_type == 'easyship_ts':
                order.write({'es_service_ids': [(2, es_service_id.id, False) for es_service_id in order.es_service_ids.filtered(lambda x: x.order_line_id.id == order_line_id.id)]})
            return results

    @http.route(['/shop/update_es_service'], type='json', auth='public', methods=['POST'], website=True, csrf=False)
    def update_es_service(self, **post):
        results = {}
        if hasattr(self, '_update_delivery_es_service'):
            results.update(self._update_delivery_es_service(**post))
        return results

    # update the service and add sale order line and then return result
    def _update_delivery_es_service(self, **post):
        order = request.website.sale_get_order()
        carrier_service_id = int(post['es_service_id'])
        order_line_id = int(post['order_line_id'])
        if order and carrier_service_id and order_line_id:
            order_line = request.env['sale.order.line'].sudo().browse(order_line_id)
            # order_line.order_id.get_delivery_price(order_line_id)
            request.env['es.service.charge'].browse(carrier_service_id).sudo().set_delivery_line(order_line=order_line)
            order_line.order_id.set_dynamic_delivery_line()
        return self._update_website_delivery_es_service(order, **post)

    def _update_website_delivery_es_service(self, order, **post):
        carrier_service_id = int(post['es_service_id'])
        currency = order.currency_id
        carrier_id = order.carrier_id
        if order and carrier_service_id:
            return {'status': order.delivery_rating_success,
                    'error_message': order.delivery_message,
                    'carrier_id': carrier_id.id,
                    'es_service_id': carrier_service_id,
                    'new_total_delivery_amount': order.amount_delivery,
                    'new_line_delivery_amount': request.env['es.service.charge'].browse(carrier_service_id).sudo().total_charge,
                    'new_amount_delivery': self._format_amount(order.delivery_price, currency),
                    'new_amount_untaxed': self._format_amount(order.amount_untaxed, currency),
                    'new_amount_tax': self._format_amount(order.amount_tax, currency),
                    'new_amount_total': self._format_amount(order.amount_total, currency),
                    }
        return {}

import logging
import requests
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    @api.multi
    def easypost_ts_prepare_request_data(self, shipper, recipient):
        res = super(DeliveryCarrier, self).easypost_ts_prepare_request_data(shipper, recipient)
        order_line_id = self.env.context.get('sale_order_line', False)
        if order_line_id:
            order_line = order_line_id and self.env['sale.order.line'].browse(order_line_id)
            if order_line.product_id.marketplace_seller_id.warehouse_id:
                warehouse_id = order_line.product_id.marketplace_seller_id.warehouse_id
                from_address = res.get('order') and res.get('order').get('from_address')
                from_address.update({
                    'name': warehouse_id.partner_id.name or '',
                    'street1': warehouse_id.partner_id.street,
                    'street2': warehouse_id.partner_id.street2 or '',
                    'city': warehouse_id.partner_id.city or '',
                    'zip': warehouse_id.partner_id.zip,
                    'phone': warehouse_id.partner_id.phone or '',
                    'email': warehouse_id.partner_id.email or '',
                    'state': warehouse_id.partner_id.state_id.name or '',
                    'country': warehouse_id.partner_id.country_id.code or '',
                })
        return res

    @api.model
    def easypost_ts_add_custom_info(self, picking=False, order=False, package=False):
        customs_items = []
        order_line_id = self.env.context.get('sale_order_line', False)
        if order_line_id:
            order_line = order_line_id and self.env['sale.order.line'].browse(order_line_id)
            if order_line.product_id.marketplace_seller_id.warehouse_id:
                origin_country = order_line.product_id.marketplace_seller_id.warehouse_id.partner_id.country_id
            else:
                origin_country = order.warehouse_id.partner_id.country_id
            customs_items.append({
                'description': order_line.product_id.name,
                'quantity': order_line.product_uom_qty,
                'value': order_line.price_subtotal,
                'currency': order.currency_id.name,
                'weight': self._easypost_ts_convert_weight(order_line.product_id.weight * order_line.product_uom_qty),
                'origin_country': origin_country.code,
                'hs_tariff_number': order_line.product_id.hs_code or '',
            })
        elif order:
            for line in order.order_line:
                if line.product_id.type not in ['product', 'consu']:
                    continue
                if line.product_id.marketplace_seller_id.warehouse_id:
                    origin_country = line.product_id.marketplace_seller_id.warehouse_id.partner_id.country_id
                else:
                    origin_country = order.warehouse_id.partner_id.country_id
                customs_items.append({
                    'description': line.product_id.name,
                    'quantity': line.product_uom_qty,
                    'value': line.price_subtotal,
                    'currency': order.currency_id.name,
                    'weight': self._easypost_ts_convert_weight(line.product_id.weight * line.product_uom_qty),
                    'origin_country': origin_country.code,
                    'hs_tariff_number': line.product_id.hs_code or '',
                })
            return customs_items
        elif picking and not package:
            for line in picking.move_line_ids:
                if line.product_id.type not in ['product', 'consu']:
                    continue
                if line.product_id.marketplace_seller_id.warehouse_id:
                    origin_country = line.product_id.marketplace_seller_id.warehouse_id.partner_id.country_id
                else:
                    origin_country = order.warehouse_id.partner_id.country_id
                customs_items.append({
                    'description': line.product_id.name,
                    'quantity': line.qty_done,
                    'value': line.move_id.sale_line_id.price_subtotal,
                    'currency': picking.sale_id.currency_id.name,
                    'weight': self._easypost_ts_convert_weight(line.product_id.weight * line.qty_done),
                    'origin_country': origin_country.code,
                    'hs_tariff_number': line.product_id.hs_code or '',
                })
        elif picking and package:
            for line in picking.move_line_ids.filtered(lambda x: x.result_package_id == package):
                if line.product_id.type not in ['product', 'consu']:
                    continue
                if line.product_id.marketplace_seller_id.warehouse_id:
                    origin_country = line.product_id.marketplace_seller_id.warehouse_id.partner_id.country_id
                else:
                    origin_country = order.warehouse_id.partner_id.country_id
                customs_items.append({
                    'description': line.product_id.name,
                    'quantity': line.qty_done,
                    'value': line.product_id.list_price * line.qty_done,
                    'currency': picking.sale_id.currency_id.name,
                    'weight': self._easypost_ts_convert_weight(line.product_id.weight * line.qty_done),
                    'origin_country': origin_country.code,
                    'hs_tariff_number': line.product_id.hs_code or '',
                })
        return customs_items

    def easypost_ts_send_shipping(self, pickings):
        res = []
        for picking in pickings:
            exact_price = 0.0
            tracking_number_list = []
            tracking_urls = []
            attachments = []
            order = picking.sale_id
            company = order.company_id or picking.company_id or self.env.user.company_id
            # is_int_shipment = False
            # if order.warehouse_id.partner_id.country_id.code != order.partner_shipping_id.country_id.code:
            #     is_int_shipment = True
            total_bulk_weight = self._easypost_ts_convert_weight(picking.weight_bulk)
            try:
                picking.check_packages_are_identical()
                request_data = self.easypost_ts_prepare_request_data(picking.picking_type_id.warehouse_id.partner_id, picking.partner_id)
                package_list = []
                is_int_shipment = False
                if request_data['order']['from_address']['country'] != order.partner_shipping_id.country_id.code:
                    is_int_shipment = True
                if picking.package_ids:
                    # Create all packages
                    for package in picking.package_ids:
                        package_weight = self._easypost_ts_convert_weight(package.shipping_weight)
                        parcel_dict = self.easypost_ts_add_parcel(package_weight)
                        if is_int_shipment:
                            customs_items = self.easypost_ts_add_custom_info(picking=picking, package=package)
                            parcel_dict.update({'customs_info': {'customs_items': customs_items}, 'reference': order.name})
                        package_list.append(parcel_dict)
                # Create one package with the rest (the content that is not in a package)
                if total_bulk_weight:
                    parcel_dict = self.easypost_ts_add_parcel(total_bulk_weight)
                    if is_int_shipment:
                        customs_items = self.easypost_ts_add_custom_info(picking)
                        parcel_dict.update({'customs_info': {'customs_items': customs_items}, 'reference': order.name})
                    package_list.append(parcel_dict)

                request_data['order'].update({'shipments': package_list, })
                response = self.shipping_partner_id.sudo()._easypost_send_request('orders', request_data, self.prod_environment, method="POST")
                service_rate = self.easypost_ts_extract_shipping_rates(response)
                if not service_rate:
                    raise Warning(_("Rate isn't available for selected service."))
                buy_request_data = {}
                buy_request_data['carrier'] = service_rate['carrier']
                buy_request_data['service'] = service_rate['service']
                buy_response = self.shipping_partner_id.sudo()._easypost_send_request('orders/%s/buy' % response['id'], buy_request_data, self.prod_environment, method="POST")
                shipment_result = buy_response['shipments']
                if shipment_result:
                    if isinstance(shipment_result, dict):
                        shipment_result = [shipment_result]
                    for shipment in shipment_result:
                        tracking_number = shipment.get('tracking_code')
                        tracking_url = shipment.get('tracker', {}).get('public_url', False)
                        label_url = shipment.get('postage_label', {}).get('label_url', False)
                        label_binary_data = requests.get(label_url).content
                        tracking_number_list.append(tracking_number)
                        tracking_url and tracking_urls.append([tracking_number, tracking_url])
                        attachments.append(
                            ('Easypost-%s.%s' % (tracking_number, self.ep_label_file_type), label_binary_data))
                exact_price = float(service_rate['rate'])
                if order.currency_id.name != service_rate['currency']:
                    rate_currency = self.env['res.currency'].search([('name', '=', service_rate['currency'])], limit=1)
                    if rate_currency:
                        exact_price = rate_currency.compute(exact_price, order.currency_id, company)
                picking.write({'ep_order_id': response['id'], 'ep_tracking_url': tracking_urls})
                msg = (_('<b>Shipment created!</b><br/>'))
                picking.message_post(body=msg, attachments=attachments)
            except Exception as e:
                raise Warning(e)
            res = res + [{'exact_price': exact_price, 'tracking_number': ",".join(tracking_number_list)}]
        return res

    @api.multi
    def easypost_ts_send_rate_request(self, order, total_weight, max_weight):
        try:
            request_data = self.easypost_ts_prepare_request_data(order.warehouse_id.partner_id, order.partner_shipping_id)
            package_list = []
            is_int_shipment = False
            if request_data['order']['from_address']['country'] != order.partner_shipping_id.country_id.code:
                is_int_shipment = True
            if max_weight and total_weight > max_weight:
                total_package = int(total_weight / max_weight)
                last_package_weight = total_weight % max_weight
                for index in range(total_package):
                    parcel_dict = self.easypost_ts_add_parcel(max_weight)
                    package_list.append(parcel_dict)
                if last_package_weight:
                    parcel_dict = self.easypost_ts_add_parcel(last_package_weight)
                    package_list.append(parcel_dict)
            else:
                parcel_dict = self.easypost_ts_add_parcel(total_weight)
                if is_int_shipment:
                    customs_items = self.easypost_ts_add_custom_info(order=order)
                    parcel_dict.update({'customs_info': {'customs_items':customs_items}, 'reference': order.name})
                package_list.append(parcel_dict)
            request_data['order'].update({'shipments': package_list})
            response = self.shipping_partner_id._easypost_send_request('orders', request_data, self.prod_environment, method="POST")
        except Exception as e:
            return {'success': False, 'price': 0.0, 'error_message': e, 'warning_message': False}
        rate_data = response.get('rates')
        if not rate_data:
            return {'success': False, 'price': 0.0, 'error_message': "Do not provide shipments for selected services. Please try with another service", 'warning_message': False}
        service_rate = self.easypost_ts_extract_shipping_rates(response)
        if not service_rate:
            return {'success': False, 'price': 0.0, 'error_message': "Rate isn't available for selected service.", 'warning_message': False}
        shipping_charge = float(service_rate['rate'])
        if order.currency_id.name != service_rate['currency']:
            rate_currency = self.env['res.currency'].search([('name', '=', service_rate['currency'])], limit=1)
            if rate_currency:
                shipping_charge = rate_currency.compute(shipping_charge, order.currency_id)
        return {'success': True,
                'price': float(shipping_charge),
                'est_delivery_days': service_rate.get('delivery_days') or 4,
                'error_message': False,
                'warning_message': False}

    def easypost_ts_rate_shipment(self, order):
        check_value = self.check_required_value_shipping_request(order)
        if check_value:
            return {'success': False, 'price': 0.0, 'error_message': check_value, 'warning_message': False}
        order_line_id = self.env.context.get('sale_order_line', False)
        if order_line_id:
            est_weight_value = sum([(line.product_id.weight * line.product_uom_qty) for line in order.order_line.filtered(lambda x: x.id == order_line_id)]) or 0.0
        else:
            est_weight_value = sum([(line.product_id.weight * line.product_uom_qty) for line in order.order_line]) or 0.0
        total_weight = self._easypost_ts_convert_weight(est_weight_value)
        max_weight = self._easypost_ts_convert_weight(self.ep_product_packaging_id.max_weight)
        return self.easypost_ts_send_rate_request(order, total_weight, max_weight)

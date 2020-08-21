import json
import logging
import requests
from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import ValidationError, Warning
from odoo.tools.float_utils import float_round

_logger = logging.getLogger(__name__)


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(selection_add=[('easypost_ts', "Easypost")])
    easypost_carrier_id = fields.Many2one('easypost.carrier', "Carrier")
    ep_carrier_name = fields.Char(related='easypost_carrier_id.name', store=True)
    ep_service_type_id = fields.Many2one("easypost.services", string="Shipping Services", domain="[('ep_carrier_name', '=', ep_carrier_name)]")
    ep_product_packaging_id = fields.Many2one("product.packaging", string="Default Package Type", domain="[('ep_carrier_name', '=', ep_carrier_name)]")
    ep_label_file_type = fields.Selection([
        ('PNG', 'PNG'), ('PDF', 'PDF'),
        ('ZPL', 'ZPL'), ('EPL2', 'EPL2')],
        string="Label File Type", default='PDF')

    @api.onchange('easypost_carrier_id')
    def on_change_easypost_carrier_id(self):
        self.ep_service_type_id = False
        self.ep_product_packaging_id = False

    @api.multi
    def easypost_ts_prepare_request_data(self, shipper, recipient):
        self.ensure_one()
        request_data = {'order':
                            {'carrier_accounts': {'id': self.easypost_carrier_id.easypost_id},
                             'from_address': {
                                 'name': shipper.name,
                                 'street1': shipper.street,
                                 'street2': shipper.street2,
                                 'city': shipper.city,
                                 'zip': shipper.zip,
                                 'phone': shipper.phone,
                                 'email': shipper.email,
                                 'state': shipper.state_id.name or '',
                                 'country': shipper.country_id.code},
                             'to_address': {
                                 'name': recipient.name,
                                 'street1': recipient.street,
                                 'street2': recipient.street2,
                                 'city': recipient.city,
                                 'zip': recipient.zip,
                                 'phone': recipient.phone,
                                 'email': recipient.email,
                                 'state': recipient.state_id.name or '',
                                 'country': recipient.country_id.code, }
                             }}
        return request_data

    @api.model
    def easypost_ts_add_parcel(self, weight):
        parcel_dict = {"parcel": {'weight': weight}, 'options': {'label_format': self.ep_label_file_type}}
        if self.ep_product_packaging_id.shipper_package_code:
            parcel_dict['parcel'].update({'predefined_package': self.ep_product_packaging_id.shipper_package_code})
        else:
            parcel_dict['parcel'].update({'length': self.ep_product_packaging_id.length, 'width': self.ep_product_packaging_id.width, 'height': self.ep_product_packaging_id.height})
        return parcel_dict

    @api.model
    def easypost_ts_add_custom_info(self, picking=False, order=False, package=False):
        customs_items = []
        if order:
            for line in order.order_line:
                if line.product_id.type not in ['product', 'consu']:
                    continue
                customs_items.append({
                    'description': line.product_id.name,
                    'quantity': line.product_uom_qty,
                    'value': line.price_subtotal,
                    'currency': order.currency_id.name,
                    'weight': self._easypost_ts_convert_weight(line.product_id.weight * line.product_uom_qty),
                    'origin_country': order.warehouse_id.partner_id.country_id.code,
                    'hs_tariff_number': line.product_id.hs_code or '',
                })
            return customs_items
        elif picking and not package:
            for line in picking.move_line_ids:
                if line.product_id.type not in ['product', 'consu']:
                    continue
                customs_items.append({
                    'description': line.product_id.name,
                    'quantity': line.qty_done,
                    'value': line.move_id.sale_line_id.price_subtotal,
                    'currency': picking.sale_id.currency_id.name,
                    'weight': self._easypost_ts_convert_weight(line.product_id.weight * line.qty_done),
                    'origin_country': picking.picking_type_id.warehouse_id.partner_id.country_id.code,
                    'hs_tariff_number': line.product_id.hs_code or '',
                })
        elif picking and package:
            for line in picking.move_line_ids.filtered(lambda x: x.result_package_id == package):
                if line.product_id.type not in ['product', 'consu']:
                    continue
                customs_items.append({
                    'description': line.product_id.name,
                    'quantity': line.qty_done,
                    'value': line.product_id.list_price * line.qty_done,
                    'currency': picking.sale_id.currency_id.name,
                    'weight': self._easypost_ts_convert_weight(line.product_id.weight * line.qty_done),
                    'origin_country': picking.picking_type_id.warehouse_id.partner_id.country_id.code,
                    'hs_tariff_number': line.product_id.hs_code or '',
                })
        return customs_items

    @api.model
    def easypost_ts_extract_shipping_rates(self, response_data):
        rate_data = response_data.get('rates')
        if not rate_data:
            return {'success': False, 'price': 0.0, 'error_message': "Do not provide shipments for selected services. Please try with another service", 'warning_message': False}
        service_rate = [rate for rate in rate_data if rate['service'] == self.ep_service_type_id.name]
        return service_rate[0] if service_rate else False

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
                'error_message': False,
                'warning_message': False}

    def _easypost_ts_convert_weight(self, weight):
        weight_uom_id = self.env['product.template']._get_weight_uom_id_from_ir_config_parameter()
        weight_lbs = weight_uom_id._compute_quantity(weight, self.env.ref('uom.product_uom_lb'), round=False)
        return float_round((weight_lbs * 16), precision_digits=1)

    def easypost_ts_rate_shipment(self, order):
        check_value = self.check_required_value_shipping_request(order)
        if check_value:
            return {'success': False, 'price': 0.0, 'error_message': check_value, 'warning_message': False}
        est_weight_value = sum(
            [(line.product_id.weight * line.product_uom_qty) for line in order.order_line]) or 0.0
        total_weight = self._easypost_ts_convert_weight(est_weight_value)
        max_weight = self._easypost_ts_convert_weight(self.ep_product_packaging_id.max_weight)
        return self.easypost_ts_send_rate_request(order, total_weight, max_weight)

    def easypost_ts_send_shipping(self, pickings):
        res = []
        for picking in pickings:
            exact_price = 0.0
            tracking_number_list = []
            tracking_urls = []
            attachments = []
            order = picking.sale_id
            company = order.company_id or picking.company_id or self.env.user.company_id
            is_int_shipment = False
            if order.warehouse_id.partner_id.country_id.code != order.partner_shipping_id.country_id.code:
                is_int_shipment = True
            total_bulk_weight = self._easypost_ts_convert_weight(picking.weight_bulk)
            try:
                picking.check_packages_are_identical()
                request_data = self.easypost_ts_prepare_request_data(picking.picking_type_id.warehouse_id.partner_id, picking.partner_id)
                package_list = []
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

    def easypost_ts_get_tracking_link(self, picking):
        tracking_urls = safe_eval(picking.ep_tracking_url)
        if len(tracking_urls) == 1:
            return tracking_urls[0][1]
        return json.dumps(tracking_urls)

    def easypost_ts_cancel_shipment(self, picking):
        raise Warning(_("Sorry! You can't cancel Easypost shipment anymore."))

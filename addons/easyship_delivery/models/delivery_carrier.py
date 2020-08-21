import json
import logging
import requests
import binascii
from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import ValidationError, Warning
from odoo.tools.float_utils import float_round

_logger = logging.getLogger(__name__)


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(selection_add=[('easyship_ts', "Easyship")])
    es_category_id = fields.Many2one("easyship.category", "Product Category")
    es_tax_duties_plaid_by = fields.Selection([('Sender', 'Sender'), ('Receiver', 'Receiver')], string="Taxes Duties Paid By", default="Sender")
    es_is_insured = fields.Boolean("Is Insured?", help="Shipment includes insurance fee")
    es_product_packaging_id = fields.Many2one('product.packaging', string="Default Package Type")

    @api.multi
    def easyship_ts_prepare_request_data(self, shipper, recipient):
        self.ensure_one()
        request_data = {
            'origin_country_alpha2': shipper.country_id.code,
            'origin_city': shipper.city or '',
            'origin_state': shipper.state_id.name or '',
            'origin_postal_code': shipper.zip or '',
            'destination_country_alpha2': recipient.country_id.code,
            'destination_city': recipient.city or '',
            'destination_state': recipient.state_id.name or '',
            'destination_postal_code': recipient.zip or '',
            'destination_address_line_1': recipient.street or '',
            'destination_address_line_2': recipient.street2 or '',
            'taxes_duties_paid_by': self.es_tax_duties_plaid_by or 'Sender',
            'is_insured': self.es_is_insured,
        }
        return request_data

    @api.multi
    def easyship_ts_prepare_request_data_for_shipment(self, picking, shipper, recipient):
        request_data = self.easyship_ts_prepare_request_data(shipper, recipient)
        request_data.update({
            'platform_order_number': picking.name,
            'destination_name': recipient.name,
            'destination_company_name': recipient.name if recipient.is_company else '',
            'destination_phone_number': recipient.phone or recipient.mobile,
            'destination_email_address': recipient.email,
        })
        return request_data

    @api.multi
    def easyship_ts_prepare_items_data(self, order=False, picking=False):
        self.ensure_one()
        item_list = []
        if order:
            for line in order.order_line.filtered(lambda line_item: not line_item.product_id.type in ['service', 'digital'] and not line_item.is_delivery):
                item_list.append({
                    'actual_weight': self._easyship_ts_convert_weight(line.product_id.weight * line.product_uom_qty),
                    'category': self.es_category_id.slug,
                    'quantity': line.product_uom_qty,
                    'declared_currency': order.currency_id.name,
                    'declared_customs_value': line.price_subtotal,
                })
        if picking:
            for line in picking.move_line_ids:
                item_list.append({
                    'description': line.product_id.name,
                    'sku': line.product_id.default_code,
                    'actual_weight': self._easyship_ts_convert_weight(line.product_id.weight * line.qty_done),
                    'category': self.es_category_id.slug,
                    'quantity': line.qty_done,
                    'declared_currency': picking.sale_id.currency_id.name,
                    'declared_customs_value': line.move_id.sale_line_id.price_subtotal,
                })
        return item_list

    @api.model
    def easyship_ts_add_parcel(self, weight):
        parcel_dict = {'length': self.es_product_packaging_id.length,
                       'width': self.es_product_packaging_id.width,
                       'height': self.es_product_packaging_id.height}
        return parcel_dict

    @api.model
    def easyship_ts_extract_shipping_rates(self, order, response_data):
        rate_data = response_data.get('rates')
        if not rate_data:
            order.es_service_ids.unlink()
            messages = response_data.get('messages', [])
            return {'success': False, 'price': 0.0, 'error_message': messages and messages[0] or "Do not provide shipments for selected services. Please try with another service", 'warning_message': False}
        if isinstance(rate_data, dict):
            rate_data = [rate_data]
        shipping_charge = 0.0
        for rate in rate_data:
            courier_id = rate.get('courier_id')
            charge_currency = rate.get('currency', 'USD')
            total_charge = rate.get('total_charge')
            shipment_charge = rate.get('shipment_charge')
            insurance_fee = rate.get('insurance_fee')
            if order.currency_id.name != charge_currency:
                rate_currency = self.env['res.currency'].search([('name', '=', charge_currency)], limit=1)
                if rate_currency:
                    total_charge = rate_currency.compute(float(total_charge), order.currency_id)
                    shipment_charge = rate_currency.compute(float(shipment_charge), order.currency_id)
                    insurance_fee = rate_currency.compute(float(insurance_fee), order.currency_id)
            prepared_vals = {
                'es_service_id': courier_id,
                'courier_name': rate.get('courier_name'),
                'min_delivery_time': rate.get('min_delivery_time'),
                'max_delivery_time': rate.get('max_delivery_time'),
                'shipment_charge': shipment_charge,
                'insurance_fee': insurance_fee,
                'total_charge': total_charge,
                'courier_does_pickup':rate.get('courier_does_pickup'),
            }
            existing_charge = order.es_service_ids.filtered(lambda x: x.es_service_id == courier_id)
            if existing_charge:
                existing_charge.write(prepared_vals)
            else:
                prepared_vals.update({'order_id': order.id})
                order.es_service_ids.create(prepared_vals)
        if order.es_service_id:
            shipping_charge = order.es_service_id.total_charge
        return {'success': True,
                'price': shipping_charge,
                'error_message': False,
                'warning_message': False}

    @api.multi
    def easyship_ts_send_rate_request(self, order, total_weight, max_weight):
        try:
            request_data = self.easyship_ts_prepare_request_data(order.warehouse_id.partner_id, order.partner_shipping_id)
            items_data = self.easyship_ts_prepare_items_data(order=order)
            request_data.update({'items': items_data})
            parcel_dict = self.easyship_ts_add_parcel(total_weight)
            request_data.update({'box': parcel_dict, 'total_actual_weight': total_weight})
            response = self.shipping_partner_id._easyship_send_request('rate/v1/rates', request_data, self.prod_environment, method="POST")
        except Exception as e:
            return {'success': False, 'price': 0.0, 'error_message': e, 'warning_message': False}
        return self.easyship_ts_extract_shipping_rates(order, response)
        # shipping_charge = float(service_rate['rate'])
        # if order.currency_id.name != service_rate['currency']:
        #     rate_currency = self.env['res.currency'].search([('name', '=', service_rate['currency'])], limit=1)
        #     if rate_currency:
        #         shipping_charge = rate_currency.compute(shipping_charge, order.currency_id)

    def _easyship_ts_convert_weight(self, weight):
        weight_uom_id = self.env['product.template']._get_weight_uom_id_from_ir_config_parameter()
        if self.env.ref('uom.product_uom_kgm').id != weight_uom_id.id:
            weight = weight_uom_id._compute_quantity(weight, self.env.ref('uom.product_uom_kgm'), round=False)
        return weight

    def easyship_ts_rate_shipment(self, order):
        check_value = self.check_required_value_shipping_request(order)
        if check_value:
            return {'success': False, 'price': 0.0, 'error_message': check_value, 'warning_message': False}
        est_weight_value = sum(
            [(line.product_id.weight * line.product_uom_qty) for line in order.order_line]) or 0.0
        total_weight = self._easyship_ts_convert_weight(est_weight_value)
        max_weight = self._easyship_ts_convert_weight(self.es_product_packaging_id.max_weight)
        return self.easyship_ts_send_rate_request(order, total_weight, max_weight)

    def easyship_ts_send_shipping(self, pickings):
        res = []
        for picking in pickings:
            exact_price = 0.0
            tracking_number_list = []
            tracking_urls = []
            attachments = []
            order = picking.sale_id
            company = order.company_id or picking.company_id or self.env.user.company_id
            total_bulk_weight = self._easyship_ts_convert_weight(picking.weight)
            try:
                request_data = self.easyship_ts_prepare_request_data_for_shipment(picking, picking.picking_type_id.warehouse_id.partner_id, picking.partner_id)
                items_data = self.easyship_ts_prepare_items_data(picking=picking)
                request_data.update({'items': items_data})
                parcel_dict = self.easyship_ts_add_parcel(total_bulk_weight)
                request_data.update({'box': parcel_dict})
                request_data.update({
                    'total_actual_weight': total_bulk_weight,
                    'selected_courier_id': picking.sale_id.es_service_id.es_service_id,
                    'buy_label_synchronous': True,
                    'label': '4x6',
                    'commercial_invoice': '4x6',
                    'packing_slip': '4x6',
                    'format': 'PDF',
                })
                response = self.shipping_partner_id.sudo()._easyship_send_request('shipment/v1/shipments/create_and_buy_label', request_data, self.prod_environment, method="POST")
                shipment_result = response.get('shipment', False)
                if not shipment_result:
                    raise Warning(_("Didn't get the shipment created in EasyShip."))

                label_response = shipment_result.get('label_response', False)
                shipping_documents = shipment_result.get('shipping_documents', {})
                label_document = shipping_documents.get('label', {}).get('base64_encoded_strings')
                packing_slip_document = shipping_documents.get('packing_slip', {}).get('base64_encoded_strings')
                commercial_invoice_document = shipping_documents.get('commercial_invoice', {}).get('base64_encoded_strings')
                exact_price = label_response.get('cost')
                tracking_number = shipment_result.get('tracking_number')
                tracking_url = shipment_result.get('tracking_page_url', False)
                tracking_number_list.append(tracking_number)
                tracking_url and tracking_urls.append([tracking_number, tracking_url])
                if label_document:
                    label_binary_data = binascii.a2b_base64(label_document[0])
                    attachments.append(
                        ('EasyShip-%s.pdf' % (tracking_number), label_binary_data))
                if packing_slip_document:
                    packing_slip_binary_data = binascii.a2b_base64(packing_slip_document[0])
                    attachments.append(
                        ('EasyShip-Slip-%s.pdf' % (tracking_number), packing_slip_binary_data))
                if commercial_invoice_document:
                    commercial_invoice_binary_data = binascii.a2b_base64(commercial_invoice_document[0])
                    attachments.append(
                        ('EasyShip-ComInv-%s.pdf' % (tracking_number), commercial_invoice_binary_data))
                if order.currency_id.name != shipment_result['currency']:
                    rate_currency = self.env['res.currency'].search([('name', '=', shipment_result['currency'])], limit=1)
                    if rate_currency:
                        exact_price = rate_currency.compute(exact_price, order.currency_id, company)
                picking.write({'es_shipment_id': shipment_result['easyship_shipment_id'], 'es_tracking_url': tracking_urls})
                msg = (_('<b>Shipment created!</b><br/>'))
                picking.message_post(body=msg, attachments=attachments)
            except Exception as e:
                raise Warning(e)
            res = res + [{'exact_price': exact_price, 'tracking_number': ",".join(tracking_number_list)}]
        return res

    def easyship_ts_get_tracking_link(self, picking):
        tracking_urls = safe_eval(picking.es_tracking_url)
        if len(tracking_urls) == 1:
            return tracking_urls[0][1]
        return json.dumps(tracking_urls)

    def easyship_ts_cancel_shipment(self, picking):
        if picking.es_shipment_id:
            self.shipping_partner_id.sudo()._easyship_send_request('shipment/v1/shipments/%s' % picking.es_shipment_id, self.prod_environment, method="DELETE")
            return True
        else:
            raise Warning(_("Sorry! EasyShip Shipment ID not found in delivery order!"))

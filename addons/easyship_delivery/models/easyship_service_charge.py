from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, Warning


class EasyshipServiceCharge(models.Model):
    _name = "es.service.charge"
    _description = 'EasyShip Service'
    _order = 'total_charge, min_delivery_time, max_delivery_time'
    _rec_name = 'courier_name'

    @api.depends('min_delivery_time', 'max_delivery_time', 'es_service_id')
    def _compute_delivery_time(self):
        for record in self:
            if record.min_delivery_time and record.max_delivery_time:
                record.delivery_time = "%s - %s working days" % (record.min_delivery_time, record.max_delivery_time)

    es_service_id = fields.Char("EasyShip Service ID", required=True, copy=False)
    courier_name = fields.Char("Service", required=True, copy=False)
    min_delivery_time = fields.Char("Min Delivery Time", copy=False)
    max_delivery_time = fields.Char("Max Delivery Time", copy=False)
    delivery_time = fields.Char("Delivery Time", compute="_compute_delivery_time", store=True)
    shipment_charge = fields.Monetary("Shipping Cost", currency_field='currency_id', copy=False)
    insurance_fee = fields.Monetary("Insurance Fee", currency_field='currency_id', copy=False)
    total_charge = fields.Monetary("Total Charge", currency_field='currency_id', copy=False)
    order_id = fields.Many2one("sale.order", string="Order", copy=False)
    currency_id = fields.Many2one(related='order_id.currency_id', depends=['order_id'], store=True, string='Currency', readonly=True)
    courier_does_pickup = fields.Boolean('Courier Does Pickup')

    def set_delivery_line(self):
        self.ensure_one()
        self.order_id.delivery_rating_success = True
        self.order_id.delivery_price = self.total_charge
        self.order_id.es_service_id = self.id
        self.order_id.set_delivery_line()

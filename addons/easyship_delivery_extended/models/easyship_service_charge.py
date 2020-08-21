from odoo import models, fields, api, _


class EasyshipServiceCharge(models.Model):
    _inherit = "es.service.charge"

    order_line_id = fields.Many2one('sale.order.line', string="Order Line", copy=False, ondelete='cascade')

    def set_delivery_line(self, order_line=False):
        self.ensure_one()
        if order_line :
            order_line.es_service_id = self.id
            order_line.delivery_charge = self.total_charge
            order_line.is_delivered = True
        else:
            self.order_id.delivery_rating_success = True
            self.order_id.delivery_price = self.total_charge
            self.order_id.es_service_id = self.id
            self.order_id.set_delivery_line()

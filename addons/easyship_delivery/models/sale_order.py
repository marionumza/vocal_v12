from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, Warning


class SaleOrder(models.Model):
    _inherit = "sale.order"

    es_service_ids = fields.One2many("es.service.charge", "order_id", string="Available EasyShip Services")
    es_service_id = fields.Many2one("es.service.charge", string="EasyShip Service", copy=False)

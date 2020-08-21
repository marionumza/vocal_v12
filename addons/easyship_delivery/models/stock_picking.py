from odoo import fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    es_tracking_url = fields.Char("EasyShip Tracking URL", copy=False)
    es_shipment_id = fields.Char("EasyShip Shipment", copy=False)

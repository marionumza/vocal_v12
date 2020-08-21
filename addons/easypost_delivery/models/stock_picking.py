from odoo import fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    ep_tracking_url = fields.Char("Easypost Tracking URL", copy=False)
    ep_order_id = fields.Char("Easypost Order", copy=False)

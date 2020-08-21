from odoo import fields, models


class ProductPackaging(models.Model):
    _inherit = 'product.packaging'

    package_carrier_type = fields.Selection(selection_add=[('easypost_ts', 'Easypost')])
    ep_carrier_name = fields.Char('Carrier', index=True)

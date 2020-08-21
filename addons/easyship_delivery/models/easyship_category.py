from odoo import models, fields, api, _


class EasyshipCategory(models.Model):
    _name = "easyship.category"
    _description = "EasyShip Category"

    name = fields.Char("Name", required=True)
    slug = fields.Char("Slug", required=True, readonly=1)

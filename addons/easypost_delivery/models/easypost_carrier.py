from odoo import models, fields, api, _


class EasypostCarrier(models.Model):
    _name = "easypost.carrier"
    _description = "Easypost Carrier"

    name = fields.Char("Name", required=True)
    easypost_id = fields.Char("ID", required=True, copy=False, readonly=1)

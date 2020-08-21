# -*- coding: utf-8 -*-
from odoo import fields, models


class EasypostServices(models.Model):
    _name = 'easypost.services'
    _description = 'Easypost Services'

    name = fields.Char('Service Level Name', index=True)
    ep_carrier_name = fields.Char('Carrier', index=True)

# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class ReaPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    ifsc_code = fields.Char('IFSC Code')

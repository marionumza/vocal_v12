# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    commission_txt = fields.Text("Commission Description")
    professional_translation_txt = fields.Text("Proffessional Translation Description")
    seo_txt = fields.Text("SEO Description")
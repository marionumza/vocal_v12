# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AmazonProduct(models.Model):
    _name = "amazon.product"

    name = fields.Char('Product Name')
    img_url = fields.Char(string="Image URL")
    link_url = fields.Char(string="Link URL")

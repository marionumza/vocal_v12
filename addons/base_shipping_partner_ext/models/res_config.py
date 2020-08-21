# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    delivery_product_id = fields.Many2one('product.product', string='Delivery Product')

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.default'].sudo().set('res.config.settings', 'delivery_product_id', self.delivery_product_id.id)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        default_delivery_product_id = self.env['ir.default'].get('res.config.settings', 'delivery_product_id')
        res.update(delivery_product_id=default_delivery_product_id)
        return res

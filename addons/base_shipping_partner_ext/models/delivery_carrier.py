from odoo import models, fields, api, _


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    is_global_delivery_method = fields.Boolean(string="Is Global?", help="is available for all sellers?", default=False, copy=False)
    marketplace_seller_id = fields.Many2one("res.partner", string="Seller", default=lambda self: self.env.user.partner_id.id if self.env.user.partner_id and self.env.user.partner_id.seller else self.env['res.partner'], copy=False,
                                            help="Owned shipping partner by specific Markerplace seller.")
    product_id = fields.Many2one('product.product', string='Delivery Product', required=False, ondelete='restrict')

    @api.model
    def create(self, vals):
        if 'marketplace_seller_id' in vals:
            default_delivery_product_id = self.env['ir.default'].sudo().get('res.config.settings', 'delivery_product_id')
            vals.update({'product_id': default_delivery_product_id})
            if self.env.user.has_group('odoo_marketplace.marketplace_seller_group'):
                self = self.sudo()
        return super(DeliveryCarrier, self).create(vals)

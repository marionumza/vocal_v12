from odoo import models, fields, api, _


class ShippingPartner(models.Model):
    _inherit = "shipping.partner"

    marketplace_seller_id = fields.Many2one("res.partner", string="Seller", default=lambda self: self.env.user.partner_id.id if self.env.user.partner_id and self.env.user.partner_id.seller else self.env['res.partner'], copy=False,
                                            help="Owned shipping partner by specific Markerplace seller.")

    # @api.multi
    # def action_delivery_method(self):
    #     self.ensure_one()
    #     default_delivery_product_id = self.env['ir.default'].sudo().get('res.config.settings', 'delivery_product_id')
    #     action = self.env.ref('delivery.action_delivery_carrier_form').read()[0]
    #     action['context'] = {'default_shipping_partner_id': self.id, 'default_delivery_type': self.provider_company, 'default_product_id': default_delivery_product_id}
    #     action['domain'] = [('shipping_partner_id', '=', self.id)]
    #     return action

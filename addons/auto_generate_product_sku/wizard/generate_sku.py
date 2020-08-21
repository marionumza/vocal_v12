from odoo import models, api, fields, _


class GenerateSKU(models.TransientModel):
    _name = "generate.sku"
    _description = "Generate SKU For Multiple Product"

    @api.multi
    def do_generate_or_update(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        product_ids = self.env['product.product'].browse(active_ids)
        for record in product_ids:
            default_code = record.create_or_update_product_sku()
            if default_code:
                record.write({'default_code': default_code})
        return {'type': 'ir.actions.act_window_close'}

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.one
    def _set_default_code(self):
        if len(self.product_variant_ids) == 1:
            default_code = self.product_variant_ids.create_or_update_product_sku()
            self.product_variant_ids.default_code = default_code or self.default_code

    @api.model
    def create(self, vals):
        if 'default_code' in vals:
            get_param = self.env['ir.config_parameter'].sudo().get_param
            auto_generate_sku = get_param('auto_generate_product_sku.auto_generate_sku')
            overwrite_sku = get_param('auto_generate_product_sku.overwrite_sku')
            if auto_generate_sku and overwrite_sku:
                del vals['default_code']
        product = super(ProductTemplate, self).create(vals)
        return product

    @api.multi
    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        if not self.env.context.get('skip', False):
            for record in self:
                if len(record.product_variant_ids) == 1:
                    default_code = self.product_variant_ids.create_or_update_product_sku()
                    if default_code:
                        record.with_context(skip=True).write({'default_code': default_code})
                else:
                    for variant in record.product_variant_ids:
                        default_code = variant.create_or_update_product_sku()
                        if default_code:
                            variant.with_context(skip=True).write({'default_code': default_code})
        return res


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def create_or_update_product_sku(self):
        self.ensure_one()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        auto_generate_sku = get_param('auto_generate_product_sku.auto_generate_sku')
        overwrite_sku = get_param('auto_generate_product_sku.overwrite_sku')
        if not auto_generate_sku:
            return False
        if self.default_code and not overwrite_sku:
            return False
        product_name = get_param('auto_generate_product_sku.product_name')
        category_name = get_param('auto_generate_product_sku.category_name')
        attributes_name = get_param("auto_generate_product_sku.attributes_name")
        seperator = get_param('auto_generate_product_sku.seperator')
        letter_case = get_param('auto_generate_product_sku.letter_case')
        sequence = get_param('auto_generate_product_sku.sequence')
        default_code_list = []
        if product_name == '1st_of_each':
            words = self.name.split()
            name_default_code = "".join(word[0] for word in words)
            default_code_list.append(name_default_code.strip())
        elif product_name:
            name_default_code = self.name[:int(product_name)]
            default_code_list.append(name_default_code.strip())

        if category_name and self.categ_id:
            default_code_list.append(self.categ_id.name[:int(category_name)].strip())

        if attributes_name and self.attribute_value_ids:
            attr_default_code = ""
            for value_id in self.attribute_value_ids:
                attr_default_code += value_id.name[:int(attributes_name)]
            default_code_list.append(attr_default_code.strip())

        if sequence:
            sequence_code = sequence + str(self.id)
            default_code_list.append(sequence_code)

        if seperator and seperator == 'no_symbol':
            default_code = "".join(default_code_list)
        else:
            default_code = "%s" % seperator.join(default_code_list)

        if letter_case:
            default_code = getattr(default_code, letter_case)()
        return default_code

    @api.model
    def create(self, vals):
        product = super(ProductProduct, self).create(vals)
        default_code = product.create_or_update_product_sku()
        if default_code:
            product.write({'default_code': default_code})
        return product

    @api.multi
    def write(self, vals):
        res = super(ProductProduct, self).write(vals)
        if not self.env.context.get('skip', False):
            for record in self:
                default_code = record.create_or_update_product_sku()
                if default_code:
                    record.with_context(skip=True).write({'default_code': default_code})
        return res

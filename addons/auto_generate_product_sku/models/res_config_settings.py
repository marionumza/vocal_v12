from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    auto_generate_sku = fields.Boolean("Automatic SKU/Internal Reference", help="Set true to configure things for to auto generate SKU")
    product_name = fields.Selection(
        [('1st_of_each', '1st letter of each word.'), ('2', 'Two letters (1st)'), ('3', 'Three letters (1st)'), ('4', 'Four letters (1st)')],
        string="Product Name", default="1st_of_each")
    category_name = fields.Selection([('2', 'Two letters (1st)'), ('3', 'Three letters (1st)'), ('4', 'Four letters (1st)')], string="Category",
                                     default="2")
    attributes_name = fields.Selection([('2', 'Two letters (1st)'), ('3', 'Three letters (1st)'), ('4', 'Four letters (1st)')], string="Attributes",
                                       default="2")
    seperator = fields.Selection([('-', 'Hyphen ( - )'), ('_', 'Underscore ( _ )'), ('/', 'Forward slash ( / )'), ('no_symbol', 'Without Symbol')],
                                 string="Seperator", default="-")
    letter_case = fields.Selection([('title', 'Title'), ('lower', 'Lower'), ('upper', 'Upper')], string="Letter Case", default="upper")
    overwrite_sku = fields.Boolean("Overwrite Existing ?")
    sequence = fields.Char(string="Sequence", default="00")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        auto_generate_sku = ICPSudo.get_param('auto_generate_product_sku.auto_generate_sku')
        product_name = ICPSudo.get_param('auto_generate_product_sku.product_name')
        category_name = ICPSudo.get_param('auto_generate_product_sku.category_name')
        attributes_name = ICPSudo.get_param("auto_generate_product_sku.attributes_name")
        seperator = ICPSudo.get_param('auto_generate_product_sku.seperator')
        letter_case = ICPSudo.get_param('auto_generate_product_sku.letter_case')
        overwrite_sku = ICPSudo.get_param('auto_generate_product_sku.overwrite_sku')
        sequence = ICPSudo.get_param('auto_generate_product_sku.sequence')
        res.update(auto_generate_sku=auto_generate_sku, product_name=product_name, category_name=category_name, attributes_name=attributes_name, seperator=seperator,
                   letter_case=letter_case, overwrite_sku=overwrite_sku, sequence=sequence)
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param('auto_generate_product_sku.auto_generate_sku', self.auto_generate_sku)
        ICPSudo.set_param('auto_generate_product_sku.product_name', self.product_name)
        ICPSudo.set_param('auto_generate_product_sku.category_name', self.category_name)
        ICPSudo.set_param("auto_generate_product_sku.attributes_name", self.attributes_name)
        ICPSudo.set_param('auto_generate_product_sku.seperator', self.seperator)
        ICPSudo.set_param('auto_generate_product_sku.letter_case', self.letter_case)
        ICPSudo.set_param('auto_generate_product_sku.overwrite_sku', self.overwrite_sku)
        ICPSudo.set_param('auto_generate_product_sku.sequence', self.sequence)

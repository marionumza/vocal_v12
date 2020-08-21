import logging
_logger = logging.getLogger(__name__)
from odoo import api, fields, models


class ElasticDomainField(models.Model):
    _name = 'elastic.domain.field'




    domain_field_id = fields.Many2one('elastic.index', string='Field Index Mapping')
    model_id = fields.Many2one('ir.model', related='domain_field_id.model_id', string='Model Name', required=True)
    field_name = fields.Many2one('ir.model.fields', string='Field Name', required=True)
    field_operator = fields.Selection([
                    ('=', '='),
                    ('!=', '!='),
                    ('like', 'like'),
                    ('true', 'is True'),
                    ('false', 'is False'),
                ],'Operator', required=True,store=True)
    field_value = fields.Char(string='Field Value')


    @api.model
    def elastic_domain_field_set(self):
        model_id = self.env['ir.model'].search([('name', '=', 'Product Template'), ('model', '=', 'product.template')])
        index_id = self.env.ref("odoo_elasticsearch.elastic_index_default_data")

        active_field_id = self.env['ir.model.fields'].search([('name', '=', 'active'), ('model_id', '=', model_id.id)])

        self.create({
            'domain_field_id':index_id.id,
            # 'model_id':model_id.id,
            'field_name':active_field_id.id,
            'field_operator':"true",

        })

        desc_field_id = self.env['ir.model.fields'].search([('name', '=', 'website_published'), ('model_id', '=', model_id.id)])
        self.create({
            'domain_field_id': index_id.id,
            # 'model_id': model_id.id,
            'field_name': desc_field_id.id,
            'field_operator': "true",

        })

        saleOk_field_id = self.env['ir.model.fields'].search([('name', '=', 'sale_ok'), ('model_id', '=', model_id.id)])
        self.create({
            'domain_field_id': index_id.id,
            # 'model_id': model_id.id,
            'field_name': saleOk_field_id.id,
            'field_operator': "true",

        })
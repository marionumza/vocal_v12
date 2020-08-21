import logging
_logger = logging.getLogger(__name__)
from odoo import api, fields, models


FIELDSDOMAIN = [("ttype","in",("char","boolean","text",'float'))]

class ElasticFieldMapping(models.Model):
    _name = 'elastic.field.mapping'

    name = fields.Char(string="Field Name",related='field_id.name', required=True, help="Name of field for creating index")
    field_mapping_id = fields.Many2one('elastic.index',string='Field Index Mapping')
    field_id = fields.Many2one('ir.model.fields', string='Model Field', required=True)
    model_id = fields.Many2one('ir.model',related='field_mapping_id.model_id', string='Model Name', required=True)
    searchable = fields.Boolean(string="Searchable", default=False)
    field_type = fields.Selection([
        ('keyword', 'keyword'),
        ('text', 'text'),
        ('double', 'double'),
        ('float', 'float'),
        ('integer', 'integer'),
        ('boolean', 'boolean'),
        ('date', 'date'),
        ('ip', 'ip'),
        ], string='Field Type',default='text',required=True)


    @api.model
    def elastic_field_set(self):
        model_id = self.env['ir.model'].search([('name','=','Product Template'),('model','=','product.template')])
        name_field_id = self.env['ir.model.fields'].search([('name','=','name'),('model_id','=',model_id.id)])
        index_id = self.env.ref("odoo_elasticsearch.elastic_index_default_data")
        field_mapping_1 = self.create({
                                        "field_mapping_id":index_id.id,
                                        "field_id":name_field_id.id,
                                        "searchable":False,
                                        "field_type":"text",
                                    })

        desc_field_id = self.env['ir.model.fields'].search([('name','=','description_sale'),('model_id','=',model_id.id)])
        field_mapping_2 = self.create({

                                        "field_mapping_id": index_id.id,
                                        "field_id": desc_field_id.id,
                                        "searchable": False,
                                        "field_type": "text",
                                    })

        active_field_id = self.env['ir.model.fields'].search([('name', '=', 'active'), ('model_id', '=', model_id.id)])

        self.create({
            'field_mapping_id': index_id.id,
            'model_id': model_id.id,
            'field_id': active_field_id.id,
            'field_type': "boolean",

        })

        desc_field_id = self.env['ir.model.fields'].search(
            [('name', '=', 'website_published'), ('model_id', '=', model_id.id)])
        self.create({
            'field_mapping_id': index_id.id,
            'model_id': model_id.id,
            'field_id': desc_field_id.id,
            'field_type': "boolean",

        })

        saleOk_field_id = self.env['ir.model.fields'].search([('name', '=', 'sale_ok'), ('model_id', '=', model_id.id)])
        self.create({
            'field_mapping_id': index_id.id,
            'model_id': model_id.id,
            'field_id': saleOk_field_id.id,
            'field_type': "boolean",

        })
        setting_id = self.env.ref("odoo_elasticsearch.elastic_search_configs_default_data")
        self.env['website'].search([], limit=1).elastic_set_id = setting_id.id














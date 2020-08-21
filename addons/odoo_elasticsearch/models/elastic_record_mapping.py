import logging
_logger = logging.getLogger(__name__)
from odoo import api, fields, models


class ElasticRecordMapping(models.Model):
    _name = 'elastic.record.mapping'

    def _get_models(self):
        return [(doc.model, doc.name) for doc in self.env["ir.model"].search([])]



    elastic_index_id = fields.Many2one('elastic.index',string="Elastic Index Name")
    model_id = fields.Many2one('ir.model', string='Model Name',related='elastic_index_id.model_id')
    record_id = fields.Integer(string="Elastic Index Id")
    index_name = fields.Char(string="Index Name",related='elastic_index_id.name')
    need_sync = fields.Boolean(string="Need To Update",default=False)
    description = fields.Text(string="Error Traceback")
    record_source = fields.Reference(selection=_get_models, string='Odoo Record',
                                     help="Source Model of the record in Mapping Table.")

    def _get_mapping_ids(self,update=False, elastic_index_id=False, model_id = False, index_name=False):
        if update:
            domain = [("elastic_index_id", "=", elastic_index_id), ("model_id", "=", model_id),
                      ("index_name", "=", index_name),("need_sync", "=", True)]
        else:
            domain = [("elastic_index_id","=",elastic_index_id),("model_id","=",model_id),("index_name","=",index_name)]
        exist_ids = self.search_read(domain, fields=["record_id"])
        return exist_ids

    @api.model
    def need_sync_action(self):
        ctx = self._context.copy()
        view_id = self.env.ref('odoo_elasticsearch.elastic_search_transient_form').id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Update Record',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'elastic.search.transient',
            "view_id": view_id,
            'target': 'new',
            'context': ctx,

        }

    def check_update_fields(self,vals):
        """this method is call from the write methods of selected model whose records is updated
        example: product.product and product.template"""
        if self.id:
            fields = []
            for f in self.elastic_index_id.field_ids:
                fields.append(f.name)
            intersectionSet = set(vals).intersection(fields)
        else:
            intersectionSet = False
        return intersectionSet
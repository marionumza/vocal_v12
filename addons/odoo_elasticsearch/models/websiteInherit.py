
from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)

class WebsiteInherit(models.Model):

    _inherit = "website"


    def _getDefaultElasticConfig(self):
        # elastic_search_configs_default_data
        return self.env['elastic.search.config'].search([], limit=1).id

    elastic_set_id = fields.Many2one("elastic.search.config",default=_getDefaultElasticConfig, string="Default Elastic Server")

    @api.model
    def _get_elasticDefaults(self):
        params = {"status":False,"message":""}
        if self.elastic_set_id:
            vals ={
                "start_limit" : self.elastic_set_id.start_limit,
                "text_color":self.elastic_set_id.text_color,
                "hover_text_color":self.elastic_set_id.hover_text_color,
                "hover_background_color":self.elastic_set_id.hover_background_color,

            }

            if self.elastic_set_id.enable_product:
                vals.update({
                    "enable_product" : True,
                    "product_index":self.elastic_set_id.product_index_id.name,
                    "prdct_sugg_position": self.elastic_set_id.prdct_sugg_position,
                    "max_prdct_sugg":self.elastic_set_id.max_prdct_sugg,
                    "max_prdct_desc": self.elastic_set_id.max_prdct_desc ,
                    "is_prdct_desc":self.elastic_set_id.is_prdct_desc,
                    "is_prdct_thumb": self.elastic_set_id.is_prdct_thumb,
                })
            params.update(vals)
        return params

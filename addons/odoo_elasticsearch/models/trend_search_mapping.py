import logging
_logger = logging.getLogger(__name__)
from odoo import api, fields, models

class TrendSearchMapping(models.Model):
    _name = 'trend.search.mapping'
    _order = "sequence"

    name = fields.Char(string="Keywords", required=True, help="Name of product")
    trend_search_mapping_id = fields.Many2one('elastic.search.config',string='Field Index Mapping')
    sequence = fields.Integer(default=5)

    @api.model
    def trend_search_map_set_default(self):
        config_id = self.env['elastic.search.config'].search([],limit=1)
        config_id.trending_state = 'enable'
        self.create({
        'name':'imac',
        'trend_search_mapping_id':config_id.id
        })

        self.create({
        'name':'ipad',
        'trend_search_mapping_id':config_id.id
        })

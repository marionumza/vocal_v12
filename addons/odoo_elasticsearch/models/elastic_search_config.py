# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
#################################################################################
import logging
_logger = logging.getLogger(__name__)
from odoo import api, fields, models
import json


PRODUCTDOMAIN = [("name","in",("product-template","product-product"))]
CATEGORYDOMAIN = [("name","=","product-public-category")]

class ElasticSearchConfiguration(models.Model):
    _name = 'elastic.search.config'

    name = fields.Char(string="Name", required=True)
    active = fields.Boolean(default=True)
    # show_in_website = fields.Boolean(default=False,String="Show in Website")
    start_limit = fields.Integer(string="Start searching after first", required=True,default=3)
    enable_product = fields.Boolean(string="Enable product Suggesstion", default=False)

    product_index_id = fields.Many2one('elastic.index', string="Product Index",help="Select the Product Elastic index used on website product search")
    prdct_sugg_position = fields.Selection([("top","Top"),("bottom","Bottom")],string="Product Suggestion position",default="top")
    max_prdct_sugg = fields.Integer(string="Max no. of product suggestions ", default=7)
    max_prdct_desc = fields.Integer(string="Max Description Characters", default=20)
    is_prdct_thumb = fields.Boolean(string="Show product thumbnail",default= False)
    is_prdct_desc = fields.Boolean(string="Show product description", default=False)

    text_color = fields.Char(string="Title Color")
    desc_color = fields.Char(string="Description Color")
    hover_text_color = fields.Char(string="Hover Text Color")
    hover_background_color = fields.Char(string="Hover Background Color")
    resize_menu = fields.Integer(string="Resize Menu", default=500)

    #crone
    cron_id = fields.Many2one('ir.cron', string="Select Cron")
    interval_number = fields.Integer(string="Interval Number", default=1)
    next_call = fields.Datetime(string='Next Execution Date')
    interval_type = fields.Selection([
        ("minutes","Minutes"),
        ("hours","Hours"),
        ("days", "Days"),
        ("weeks", "Weeks"),
        ("months", "Months")
    ],string="Interval Unit")
    cron_state = fields.Selection([
        ("start","Start"),
        ("stop","Stop"),
    ],string="cron State")

    # for trending and recent search
    trend_search_mapping_ids = fields.One2many('trend.search.mapping', 'trend_search_mapping_id', string='Trending Search Keys', )
    trending_state = fields.Selection([
        ("create", "Create"),
        ("enable", "Enable"),
        ("disable","Disable"),
        ("delete", "Delete"),
        ("error", "Error"),
    ],string="Trending Search State",default="delete")


    @api.multi
    def start_crone(self):
        self.cron_id.active = True
        self.cron_id.interval_number = self.interval_number
        self.cron_id.interval_type = self.interval_type
        self.cron_id.nextcall = self.next_call
        self.cron_state = "start"

    @api.multi
    def stop_crone(self):
        self.cron_id.active = False
        self.cron_state = "stop"


    @api.model
    def process_index_update_scheduler_queue(self):
        elastic_indexObj = self.env['elastic.index'].sudo().search([])
        for obj in elastic_indexObj:
            if obj.state == "done":
                result = obj._allDataImport(crone=True)
                _logger.info("---CRON--update_result--%r----------", result)

    @api.model
    def connectionInfo(self):
        record = self.env['elastic.connection'].sudo().search([], limit=1)
        connectionStatus = record.check_connection(record)
        _logger.info("-----connectionStatus--%r----",connectionStatus)
        return connectionStatus


    # for trending and recent search models methods

    def fetch_trending_search(self):
        """whatever you return in the array of this funtion it will appear in the trending search"""
        trend = []
        elstConfigobj = self.env['elastic.search.config'].sudo().search([], limit=1)
        if elstConfigobj.trending_state == 'enable':
            products = self.env['trend.search.mapping'].sudo().search_read([],fields=['name'])
            trend = [i.get('name') for i in products]
        return json.dumps(trend)



    def create_trend_index(self):
        result = {}
        index = "trending-key-v11"
        doc_type = "product"
        connection = self.env['elastic.connection']._getConnectionData()
        if connection.get("status"):
            mapping = {
                "mappings": {
                    doc_type: {
                        "properties": {
                            'key': {'type': u'text', "fielddata": True},
                            "date": {
                                "type": "date",
                                "format": "yyyy/MM/dd HH:mm:ss"
                            }

                        }
                    }
                }
            }
            esObj = connection['elastic_obj']
            mapResult = esObj.indices.create(index=index, ignore=400, body=mapping)
            if mapResult.get("acknowledged"):
                self.trending_state = 'create'
                msg = "Trending product index is Successfully created in elastic server"
                self.trending_state = 'create'
            else:
                self.trending_state = "error"
                msg = "Trending product index is failed to created in elastic server"
        else:
            msg = connection['message']
        return self.show_msg_wizard(msg)


    @api.multi
    def enable_trend_search(self):
        self.trending_state = 'enable'

    @api.multi
    def disable_trend_search(self):
        self.trending_state = 'disable'



    def delete_trend_index(self):
        index = "trending-key-v11"
        result = self.env['elastic.connection']._getConnectionData()
        if result['status']:
            esObj = result['elastic_obj']
            del_status = esObj.indices.delete(index=index, ignore=[400, 404])
            msg = "Successfully deleted Trending product index from the Elastic server"
            self.trending_state = 'delete'
            trend_srch_mapping_ids = self.env['trend.search.mapping'].sudo().search([])
            for trnd in trend_srch_mapping_ids:
                trnd.unlink()
            return self.show_msg_wizard(msg)
        else:
            msg = result['message']
            return self.show_msg_wizard(msg)


    @api.multi
    def sycronise_trend_search(self):
        context = dict(self._context or {})
        context['elastic_search_config_id'] = self.id
        form_id = self.env.ref('odoo_elasticsearch.trend_map_wizard_form', False)
        return {
            'name': 'Synchronize your Trending Search',
            'type': 'ir.actions.act_window',
            'res_model': 'trend.map.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'views': [(form_id.id, 'form')],
            'view_id': 'form_id.id',
            'context':context,
        }



    def show_msg_wizard(self,msg):
        partial_id = self.env['wk.wizard.message'].create({'text': msg})
        return {
            'name': "Message",
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'wk.wizard.message',
            'res_id': partial_id.id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
        }

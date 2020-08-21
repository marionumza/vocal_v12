import logging
_logger = logging.getLogger(__name__)
from odoo import api, fields, models

class TrendMapWizard(models.TransientModel):
    _name = 'trend.map.wizard'


    limit = fields.Integer(string='Limit',default=5,required=True)
    start_date = fields.Datetime(string='To date',required=True)
    end_date = fields.Datetime(string='From date',required=True)


    @api.multi
    def import_trend_search(self):
        result = self.env['elastic.connection']._getConnectionData()
        if result['status']:
            esObj = result['elastic_obj']
            index = "trending-key-v11"
            doc_type = "product"
            doc ={
                    'query': {
                            "range": {
                                    "date": {
                                        "gte":self.start_date.replace("-","/"),
                                        "lte":self.end_date.replace("-","/"),
                                        "boost" : 2.0
                                        }
                                    }
                        },
                    "aggs": {
                                "keys": {
                                    "terms": {
                                        "field": "key",
                                        "order": {"_count": "desc"},
                                        "size": self.limit
                                    }
                                }
                    }
            }
            try:
                get_data = esObj.search(index=index, doc_type=doc_type, body=doc, scroll='1m')
                trend_list = [i.get('key') for i in get_data.get('aggregations').get('keys').get('buckets')]
                self._createTrendSearchMap(trend_list,self._context.get('elastic_search_config_id'))
                msg = "No Trend keys found in elastic server." if len(trend_list) < 1 else "%s Trend key(s) imported from elastic server"%len(trend_list)
                # msg = "%s are sucessfully added to Trending Product."%len(trend_list)
            except Exception as e:
                msg = str(e)
            return self.show_msg_wizard(msg)
        else:
            return self.show_msg_wizard(str(result))



    def _createTrendSearchMap(self,product_names,elastic_search_config_id):
        TrendSearchMapObj = self.env['trend.search.mapping'].sudo()
        ids = [TrendSearchMapObj.create({'name':name,'trend_search_mapping_id':elastic_search_config_id}) for name in product_names ]

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




# aggregation aggregation
    # {
    #     "aggs": {
    #         "names": {
    #             "terms": {
    #                 "field": "name",
    #                 "order": {"_count": "desc"},
    #                 "size": 1
    #             }
    #         }
    #     }
    # }






# {
#                 'size': self.limit,
#                 'query': {
#                     "range": {
#                                     "date": {
#                                         "gte":self.start_date.replace("-","/"),
#                                         "lte":self.end_date.replace("-","/"),
#                                         "boost" : 2.0
#                                     }
#                             }
#                 }
#             }





#
# {
#                 'size': self.limit,
#                 'query': {
#                     'match_all': {}
#                 }
#             }

# doc = {
#     'size': self.limit,
#     'query': {
#         "range": {
#                         "date": {
#                             "gte":self.start_date.replace("-","/"),
#                             "lte":self.end_date.replace("-","/"),
#                             "boost" : 2.0
#                         }
#                 }
#     }
# }



# {
#     "size": self.limit,
#     "query": {
#         "filtered": {
#             "query": {
#                 "match_all": {}
#             },
#             "filter": {
#                 "range": {
#                     "date": {
#                         "gte":self.start_date.replace("-","/"),
#                         "lte":self.end_date.replace("-","/"),
#                     }
#                 }
#             }
#         }
#     }
# }



# {
#     "size": 5,
#     "query": {
#         "match_all": {}
#     }
# }

#
# https://stackoverflow.com/questions/25093995/elastic-search-date-range-aggregation
# http://192.168.1.57:5601/app/kibana#/dev_tools/console?load_from=https:%2F%2Fwww.elastic.co%2Fguide%2Fen%2Felasticsearch%2Freference%2Fcurrent%2Fsnippets%2Fsearch-aggregations-bucket-terms-aggregation%2F4.json&_g=()
#
# http://192.168.1.57:5601/app/kibana#/management/kibana/indices/988ce730-ff7f-11e7-ba3a-dbf15e3c6c76?_g=()&_a=(tab:indexedFields)

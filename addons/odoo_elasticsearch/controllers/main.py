from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import http, tools, _
from odoo.http import request
import logging
_logger = logging.getLogger(__name__)
from datetime import datetime, timedelta



class WebsiteSale(WebsiteSale):

    @http.route([
            '/shop',
            '/shop/page/<int:page>',
            '/shop/category/<model("product.public.category"):category>',
            '/shop/category/<model("product.public.category"):category>/page/<int:page>'
    ], type='http', auth="public", website=True)
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        elstConfigobj = request.env['elastic.search.config'].sudo().search([],limit=1)
        result = super(WebsiteSale,self).shop(page,category=category,search=search,ppg=ppg,**post)
        connection = request.env['elastic.connection'].sudo()._getConnectionData()
        if search and connection['status'] and elstConfigobj.trending_state == 'enable':
            esObj = connection['elastic_obj']
            doc_type = "product"
            index = "trending-key-v11"
            obj = {
                'key': search,
                'date': datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
            }
            try:
                exist = esObj.index(index=index, doc_type=doc_type,body=obj)
            except Exception as e:
                _logger.info("-----<Elastic Search : Exception>---%r------",str(e))
        return result

    # @http.route('/shop/elasticSearch', auth='public', type='json', website=True, methods=['POST'])
    # def elasticSearch(self, srch, **kw):
    #     searchQuery = {
    #                     "bool": {
    #                             "filter": [
    #                             {
    #                                 "term": {
    #                                     "website_published": "true"
    #                                 }
    #                             },
    #                             {
    #                                 "term": {
    #                                     "sale_ok": "true"
    #                                 }
    #                             },
    #                             {
    #                                 "term": {
    #                                     "active": "true"
    #                                 }
    #                             },
    #                             ],
    #                             "must": {
    #                                 "simple_query_string" : {
    #                                                      "query": srch + "*",
    #                                                     "fields": ["name"],
    #                                                     "default_operator": "and"
    #                                                   }
    #                             }
    #                         }
    #                   }
    #
    #
    #     params = request.website._get_elasticDefaults()
    #     connection = request.env["elastic.connection"].sudo()._getConnectionData()
    #     get_data = []
    #     es = connection['elastic_obj']
    #     try:
    #         if params.get("enable_product"):
    #             get_product = es.search(
    #                 index=params.get("product_index"),
    #                 body={"query": searchQuery},
    #                 size=params.get("max_prdct_sugg")
    #             )
    #             get_data.append(get_product)
    #     except Exception as e:
    #         _logger.info("< Elastic Exception e > : %r", e)
    #     get_data = get_data
    #     return get_data





        # searchQuery = {
        #     "simple_query_string": {
        #         "fields": [
        #             "name",
        #             # "description_sale"
        #         ],
        #         "default_operator": "and",
        #         "query": srch + "*",
        #     }
        # }




        # get_data = es.search(index=index, body={"query":{"fuzzy_like_this_field": {"name":{"like_text": srch,"max_query_terms": 5}}}})
        # doc = {
        #     'size': 100,
        #     'query': {
        #         'match_all': {}
        #     }
        # }
        # get_data = es.search(index=indexDetail.get("index"), doc_type=indexDetail.get("doc_type"), body=doc, scroll='1m')




        # searchQuery = {"prefix": {"name": srch}}
        # searchQuery = {
        #                     "query_string": {
        #                         "default_field": "name",
        #                         "query": srch
        #                     }
        #                 }

        # searchQuery = {
        #                     "match_phrase": {
        #                         "name": srch
        #                     }
        #               }


# ----domain-----[('sale_ok', '=', True), '|', '|', '|', ('name', 'ilike', u'ice'), ('description', 'ilike', u'ice'), ('description_sale', 'ilike', u'ice'), ('product_variant_ids.default_code', 'ilike', u'ice')]---

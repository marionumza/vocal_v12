# -*- coding: utf-8 -*-
#################################################################################
# Author : Webkul Software Pvt. Ltd. (<https://webkul.com/>:wink:
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>;
#################################################################################
{
    'name'		    : 'Smart search using Elasticsearch',
    'description'	: """ Smart Search like a Google with Elasticsearch """,
    'summary'       :"""  Improve user experience by offering fast, accurate search results. """,
    "category"		: "Website",
    "version" 		: "1.2.0",
    "author" 		: "Webkul Software Pvt. Ltd.",
    "maintainer"	: "Saurabh Gupta",
    "website" 		: "https://webkul.com/blog/odoo-elasticsearch/",
    "live_test_url" : "http://odoodemo.webkul.com/?module=odoo_elasticsearch&version=12.0&custom_url=/shop",
    "license"       :  "Other proprietary",
    'depends'		: [
                        'website_sale',
                        'wk_wizard_messages'
                       ],
    'data'		    :[
                            'security/ir.model.access.csv',
                            'views/elastic_index_view.xml',
                            'views/elastic_record_mapping_view.xml',
                            'views/elastic_search_config_view.xml',
                            'views/header_template.xml',
                            'data/server_action_view.xml',
                            'views/elastic_search_transient_view.xml',
                            'views/website_res_config_view.xml',
                            'views/elastic_connection_view.xml',
                            'views/elastic_field_mapping_view.xml',
                            'views/default_demo_data.xml',
                            'data/demo_data_connection.xml',
                            'views/trend_map_wizard_view.xml',
    ],
    'demo'		    : [

                        ],
    "images" 		: ['static/description/banner.png'],
    "application" 	: True,
    "installable" 	: True,
    "price"		   	: 149,
    "currency"	   	: "EUR",
    "sequence"		: 1,
}

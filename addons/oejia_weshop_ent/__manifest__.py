# -*- coding: utf-8 -*-
{
    'name': "Odoo电商微信小程序企业版",
    'version': '1.0.0',
    'category': '',
    'summary': '微信小程序商城企业版扩展',
    'author': 'Oejia',
    'website': 'http://www.oejia.net/',
    'application': True,
    'depends': ['oejia_weshop', 'sale_stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_product_views.xml',
        'views/product_template_views.xml',
        'views/oe_logistics_views.xml',
        'views/wxapp_config_views.xml',
    ],
    'demo': [
    ],
    'images': [],
    'description': """
    """,
    'license': 'GPL-3',
}

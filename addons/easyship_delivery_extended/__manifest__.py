# -*- coding: utf-8 -*-
{
    'name': 'Easyship Odoo Shipping Integration Extended',
    'version': '12.0',
    'category': 'Warehouse',
    'summary': 'Extended app for Easyship',

    'depends': ['easyship_delivery', 'shipping_per_product', 'odoo_marketplace'],

    'data': [
        'views/assets.xml',
        'views/sale_order_view.xml',
    ],

    'images': ['static/description/easyship_odoo.png'],

    'author': 'Teqstars',
    'website': 'https://teqstars.com',
    'support': 'info@teqstars.com',
    'maintainer': 'Teqstars',
    "description": """
        """,

    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'OPL-1',
}

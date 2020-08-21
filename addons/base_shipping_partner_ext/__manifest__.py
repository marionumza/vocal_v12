# -*- coding: utf-8 -*-
{
    'name': 'Shipping Partners Marketplace Features',
    'version': '12.0',
    'summary': 'Allows to connect Odoo with multiple shipping providers.',
    'category': 'Warehouse',

    'depends': ['base_shipping_partner', 'odoo_marketplace', 'shipping_per_product'],
    'data':[
            'views/shipping_partner_view.xml',
            'security/ir.model.access.csv',
            'security/shipping_partner_security.xml',
            'security/delivery_carrier_security.xml',
            'views/delivery_carrier_view.xml',
            'views/res_config_view.xml',
    ],

    'images': ['static/description/base_shipping.png'],

    'author': 'Teqstars',
    'website': 'https://teqstars.com',
    'support': 'info@teqstars.com',
    'maintainer': 'Teqstars',
    "description": """""",

    'demo': [],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'OPL-1',
}

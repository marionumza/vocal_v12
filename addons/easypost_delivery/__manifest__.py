# -*- coding: utf-8 -*-
{
    'name': 'Easypost Odoo Shipping Integration',
    'version': '12.0',
    'category': 'Warehouse',
    'summary': 'Integrate & Manage your Easypost Shipping Operations from Odoo',

    'depends': ['base_shipping_partner'],

    'data': [
        'data/easypost.services.csv',
        'data/product.packaging.csv',
        'security/ir.model.access.csv',
        'views/shipping_partner_view.xml',
        'views/delivery_carrier_view.xml', ],

    'images': ['static/description/easypost_odoo.png'],

    'author': 'Teqstars',
    'website': 'https://teqstars.com',
    'support': 'info@teqstars.com',
    'maintainer': 'Teqstars',
    "description": """
        - Manage your Easypost operation from Odoo
        - Integration Easypost
        - Connector Easypost
        - Easypost Connector
        - Odoo Easypost Connector
        - Easypost integration
        - Easypost odoo connector
        - Easypost odoo integration
        - Easypost shipping integration
        - Easypost integration with Odoo
        - odoo integration apps
        - odoo Easypost integration
        - odoo integration with Easypost
        - shipping integation
        - shipping provider integration
        - shipper integration
        - Easypost shipping 
        - Easypost delivery
        - USPS, UPS, FedEx, DHL eCommerce, DHL Express, LaserShip, OnTrac, GSO, APC, Aramex, ArrowXL, Asendia, Australia Post, AxlehireV3, BorderGuru, Cainiao, Canada Post
, Canpar, CDL Last Mile Solutions, Chronopost, Colis Privé, Colissimo, Correios, CouriersPlease, Dai Post, Deliv, Deutsche Post, DPD UK, DPD
        """,

    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1',
    'price': '90.00',
    'currency': 'EUR',
    'live_test_url': 'http://bit.ly/2nuyKPu',
}

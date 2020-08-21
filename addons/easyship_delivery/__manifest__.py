# -*- coding: utf-8 -*-
{
    'name': 'Easyship Odoo Shipping Integration',
    'version': '12.0',
    'category': 'Warehouse',
    'summary': 'Integrate & Manage your EasyShip Shipping Operations from Odoo',

    'depends': ['base_shipping_partner'],

    'data': [
        'security/ir.model.access.csv',
        'views/shipping_partner_view.xml',
        'views/delivery_carrier_view.xml',
        'views/sale_order_view.xml',
        'views/es_service_charge_view.xml',
    ],

    'images': ['static/description/easyship_odoo.png'],

    'author': 'Teqstars',
    'website': 'https://teqstars.com',
    'support': 'info@teqstars.com',
    'maintainer': 'Teqstars',
    "description": """
        - Manage your Easyship operation from Odoo
        - Integration Easyship
        - Connector Easyship
        - Easyship Connector
        - Odoo Easyship Connector
        - Easyship integration
        - Easyship odoo connector
        - Easyship odoo integration
        - Easyship shipping integration
        - Easyship integration with Odoo
        - odoo integration apps
        - odoo Easyship integration
        - odoo integration with Easyship
        - shipping integation
        - shipping provider integration
        - shipper integration
        - Easyship shipping 
        - Easyship delivery
        - USPS, UPS, FedEx, DHL eCommerce, DHL Express, LaserShip, OnTrac, GSO, APC, Aramex, ArrowXL, Asendia, Australia Post, AxlehireV3, BorderGuru, Cainiao, Canada Post
, Canpar, CDL Last Mile Solutions, Chronopost, Colis Privé, Colissimo, Correios, CouriersPlease, Dai Post, Deliv, Deutsche Post, DPD UK, DPD
        """,

    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1',
    'price': '140.00',
    'currency': 'EUR',
}

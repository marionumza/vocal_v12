# -*- coding: utf-8 -*-
{
    'name': 'Auto Generate Product SKU or Internal Reference',
    'version': '12.0',
    'category': 'Sales',
    'summary': 'Odoo will automatically assign SKU or Internal Reference in Product for you.',

    'depends': ['sale_management'],

    'data': [
        'views/res_config_settings_view.xml',
        'wizard/generate_sku_view.xml'
    ],

    'images': ['static/description/auto_sku_banner.png'],

    'author': 'Teqstars',
    'website': 'https://teqstars.com',
    'support': 'info@teqstars.com',
    'maintainer': 'Teqstars',
    "description": """
        - Auto Generate SKU
        - Auto Generate Code
        - Auto Generate Internal Reference
        - Auto Generate Product SKU
        - Auto Generate Product Code
        - Auto Generate Product Internal Reference
        - Product SKU
        - Product Internal Reference
        - Product Code
        - Product Default Code
        """,

    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1',
    'price': '9.00',
    'currency': 'EUR',
}

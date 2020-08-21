# -*- coding: utf-8 -*-
{
    "name": "Amazon Odoo Affiliate Integration",
    'summary': """Amazon Odoo Affiliate Integration""",
    "category": "Website",
    "version": "1.0.0",
    "author": "",
    "license": "Other proprietary",
    "maintainer": "",
    "website": "",
    "description": """Odoo Affiliate Extension for Amazon Affiliate Management""",
    "live_test_url": "",
    "depends": [
        'website_sale'
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/amazon_affiliate_template.xml',
        'views/amazon_product_view.xml'
    ],
    # "demo": ['data/demo_data_view.xml'],
    # "images": ['static/description/Banner.png'],
    "application": True,
    "installable": True,
    'sequence': 1
}

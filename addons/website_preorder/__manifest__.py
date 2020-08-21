# -*- coding: utf-8 -*-
#################################################################################
#
# Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>:wink:
# See LICENSE file for full copyright and licensing details.
#################################################################################
{
    "name": "Website Pre-Order",
    "summary": "This module helps to order the product which are out of stock and available for pre-order.",
    "category": "Website",
    "version": "1.0.0",
    "sequence": 1,
    "author": "Webkul Software Pvt. Ltd.",
    "license": "Other proprietary",
    "website": "https://store.webkul.com/Odoo-Website-Pre-Order.html",
    "description": "https://webkul.com/blog/odoo-website-pre-order/",
    "live_test_url": "http://odoodemo.webkul.com/?module=website_preorder&version=12.0&lout=1&custom_url=/",
    "depends": [
        'website_sale',
        'website_stock',
        'website_sale_delivery',
    ],
    "data": [
        'security/ir.model.access.csv',
        'security/website_preorder_security.xml',
        'data/pre_order_mail_template.xml',
        'data/preorder_config_demo.xml',
        'wizard/notify_preorder_line.xml',
        'views/res_config_view.xml',
        'views/template.xml',
        'views/webkul_addons_config_inherit_view.xml',
        'views/inherit_product_view.xml',
    ],
    "demo": [
        'data/preorder_product_demo.xml',
        'demo/sale_order_demo_data.xml',
    ],
    "images": ['static/description/Banner.png'],
    "application": True,
    "installable": True,
    "auto_install": False,
    "price": 60,
    "currency": "EUR",
    "pre_init_hook": "pre_init_check",
}

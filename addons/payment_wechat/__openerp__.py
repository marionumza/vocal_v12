# -*- coding: utf-8 -*-

{
    'name': 'Wechat Payment Acquirer',
    'category': 'Website',
    'summary': 'Odoo 微信支付模块',
    'version': '1.0',
    'description': """Payment Acquirer: Wechat Implementation""",
    'author': 'Oejia',
    'website': 'http://www.oejia.net/',
    'depends': ['payment', 'payment_ext'],
    'data': [
        'views/weixin.xml',
        'views/payment_acquirer.xml',
        'data/weixin.xml',
    ],
    'installable': True,
    'price': 120,
    'currency': 'EUR',
    'images': [],
    'license': 'GPL-3',
    'application': True,
}

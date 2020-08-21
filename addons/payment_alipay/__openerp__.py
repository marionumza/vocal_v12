# -*- coding: utf-8 -*-

{
    'name': '支付宝支付',
    'category': 'Website',
    'summary': 'Alipay Implementation',
    'version': '1.0',
    'description': """支付宝支付,包含二维码及扫条码等支付方式的支持""",
    'author': 'Oejia',
    'website': 'http://www.oejia.net/',
    'depends': ['payment', 'payment_ext'],
    'data': [
        'views/alipay.xml',
        'views/payment_acquirer.xml',
        'data/alipay.xml',
    ],
    'installable': True,
}

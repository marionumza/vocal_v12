{
    'name': "Paypal - Unsupported Currency Support",

    'summary': """
Pay unsupported currencies with Paypal""",

    'summary_vi_VN': """
Thanh toán Paypal cho các khoản tiền tệ không nằm trong danh mục tiền tệ được Paypal hỗ trợ
    	""",

    'description': """
The problem
===========
Paypal supports a limited number of currencies that causes problems when your customer pays their invoice in a currency
that does not supoprted by Paypal.

Here is the list of currencies that supported by Paypal: https://developer.paypal.com/docs/api/reference/currency-codes/

What this module does
=====================
When customer carries out payment in a currency that is not supported by PayPal, this module will convert the payment
amount into an amount in a currency (which is configurable) that is supported by Paypal before sending the payment data
to Paypal.

During payment processing and payment notification, this module ensures that the converted amount is equavalent to the orginal one for full reconciliation.

During reconciliation, the difference due to exchange rate will be encoded into the exchange rate journal

Example
-------

1. Assume that

   * Company currency is VND (Vietnam Dong - đ), which is not a currency supported by Paypal
   * Invoice INV/2019/0001 is amounted 2,000,010đ (in VND)
   * The Paypal acquired is configured with USD as the default currency for conversion this case 
   * Exchange rate between VND/USD: 23,100

2. Payment processing

   * Convert VND to USD: 2,000,010  / 23,100 = 86.580519481, and will be rounded into 86.58
   * Request Paypal to process payment for the $86.58
   * After processing, Paypal notifies Odoo with sucess processing of the amount of $86.58.
   * Odoo verifies this amount and generate a payment of $86.58 and posted with value of $86.58 * 23,100 = 1,999,998đ
   * During reconciliation, the diffence of 12đ (between 1,999,998đ and 2,000,010đ) will be encoded into the exchange rate different. The corresponding invoice will be set to paid.


Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'author': "T.V.T Marine Automation (aka TVTMA)",
    'website': "https://www.tvtmarine.com",
    'live_test_url': "https://v12demo-int.erponline.vn",
    'support': "support@ma.tvtmarine.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['payment_paypal'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/payment_acquirer_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'images' : [
    	# 'static/description/main_screenshot.png'
    	],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}

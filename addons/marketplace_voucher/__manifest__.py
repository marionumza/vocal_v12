# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

{
    'name'          :   'Odoo Marketplace Voucher',
    'summary'       :   'Facilitates increase in sales of marketplace products by offering Vouchers/Coupon codes to customers.',
    'version'       :   '1.0.5',
    'category'      :   'Website',
    'sequence'      :   1,
    'website'       :   'https://store.webkul.com/Odoo-Marketplace-Vouchers.html',
    'description'   :   """https://webkul.com/blog/odoo-marketplace-vouchers/""",
    'author'        :   'Webkul Software Pvt. Ltd.',
    'license'       :   'Other proprietary',
    'live_test_url' :   'http://odoodemo.webkul.com/?module=marketplace_voucher&version=12.0&lifetime=120&lout=1&custom_url=/',
    'depends'       :   [
        'odoo_marketplace',
        'website_voucher',
    ],
    'data'          :   [
        'security/ir.model.access.csv',
        'security/access_control_security.xml',
        'views/mp_gift_voucher_views.xml',
        'views/inherit_templates.xml',
        'views/templates.xml',
    ],
    'images'        :  ['static/description/Banner.png'],
    'installable'   :   True,
    'auto_install'  :   False,
    'price'         :   35,
    'currency'      :   'EUR',
    'application'   :   True,
    'pre_init_hook' :   'pre_init_check',
}

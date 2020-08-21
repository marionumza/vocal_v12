#  -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE URL <https://store.webkul.com/license.html/> for full copyright and licensing details.
#################################################################################
{
  "name"                 :  "Website Coupons & Vouchers",
  "summary"              :  "Promote your business by offering Vouchers/Promotional-codes, without using pricelists.",
  "category"             :  "Website",
  "version"              :  "5.0.1",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Website-Voucher.html",
  "description"          :  """http://webkul.com/blog/odoo-website-coupons-vouchers/""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=website_voucher&version=12.0&custom_url=/shop/cart",
  "depends"              :  [
                             'wk_coupons',
                             'website_sale_delivery',
                            ],
  "data"                 :  [
                            'views/coupon_inherited_view.xml',
                             'views/templates.xml',
                             'views/inherited_sale_order_view.xml',
                             'wizard/voucher_wizard_view.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  124,
  "currency"             :  "EUR",
  "pre_init_hook"        :  "pre_init_check",
}
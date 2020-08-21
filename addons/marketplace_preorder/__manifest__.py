# -*- coding: utf-8 -*-
##########################################################################
# 2010-2017 Webkul.
#
# NOTICE OF LICENSE
#
# All right is reserved,
# Please go through this link for complete license : https://store.webkul.com/license.html
#
# DISCLAIMER
#
# Do not edit or add to this file if you wish to upgrade this module to newer
# versions in the future. If you wish to customize this module for your
# needs please refer to https://store.webkul.com/customisation-guidelines/ for more information.
#
# @Author        : Webkul Software Pvt. Ltd. (<support@webkul.com>)
# @Copyright (c) : 2010-2017 Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# @License       : https://store.webkul.com/license.html
#
##########################################################################

{
    "name"                 :  "Odoo Marketplace Pre-Order",
    "summary"              :  "This module helps to order the product which are out of stock and available for pre-order.",
    "category"             :  "Website",
    "version"              :  "1.0.1",
    "sequence"             :  11,
    "author"               :  "Webkul Software Pvt. Ltd.",
    "license"              :  "Other proprietary",
    "website"              :  "https://store.webkul.com/Odoo-Marketplace-Pre-Order.html",
    "description"          :  "https://webkul.com/blog/odoo-marketplace-pre-order/",
    "live_test_url"        :  "http://odoodemo.webkul.com/?module=marketplace_preorder&version=12.0&lifetime=120&lout=1&custom_url=/",
    "depends"              :  ['odoo_marketplace','website_preorder'],
    "data"                 :  [
                                'data/mp_preorder_data.xml',
                                'views/res_config_view.xml',
                                'views/seller_dashboard_product_view.xml',
    ],
    "images"               :  ['static/description/Banner.png'],
    "application"          :  True,
    "installable"          :  True,
    "auto_install"         :  False,
    "price"                :  25,
    "currency"             :  "EUR",
    "pre_init_hook"        :  "pre_init_check",
}

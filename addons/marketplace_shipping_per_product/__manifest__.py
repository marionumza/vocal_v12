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
  "name"                 :  "Odoo Marketplace Shipping Per Product",
  "summary"              :  "This module allows seller to add different delivery methods for their product and customer can select delivery method for each product separately and delivery amount will be calculated for each product.",
  "category"             :  "Website",
  "version"              :  "1.0.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "Odoo Marketplace Shipping Per Product",
  "description"          :  """Odoo Marketplace Shipping Per Product""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=marketplace_shipping_per_product&version=12.0",
  "depends"              :  [
                             'shipping_per_product',
                             'odoo_marketplace',
                            ],
  "data"                 :  [
                                'views/inherit_mp_product_view.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  25,
  "currency"             :  "EUR",
  "pre_init_hook"        :  "pre_init_check",
}

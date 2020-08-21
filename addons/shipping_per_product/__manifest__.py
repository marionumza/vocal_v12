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
  "name"                 :  "Shipping Per Product",
  "summary"              :  "This module allows customer to select delivery method for each product separately and delivery amount will be calculated for each product.",
  "category"             :  "Website",
  "version"              :  "1.0.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "Shipping Per Product",
  "description"          :  """Shipping Per Product""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=shipping_per_product&version=12.0",
  "depends"              :  [
                             'website_sale_delivery',
                            ],
  "data"                 :  [
                                'data/demo_sale_order.xml',
                                'views/inherit_delivery_view.xml',
                                'views/inherit_product_view.xml',
                                'views/inherit_sale_view.xml',
                                'views/inherit_sol_template.xml',
                                'wizard/sol_carrier_wizard_view.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  75,
  "currency"             :  "EUR",
  "pre_init_hook"        :  "pre_init_check",
}

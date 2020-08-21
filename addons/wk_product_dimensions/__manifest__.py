# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
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
  "name"                 :  "Product Dimensions",
  "summary"              :  "Odoo Product Dimensions allows admin to specify dimension attributes for products and providing more product details.",
  "category"             :  "Website",
  "version"              :  "1.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo.html",
  "description"          :  """Offer dimension attribute like product height
product length
product width
measure unit
weight units of measure 
dimension units measure for products
Product Dimensions
Odoo Product Dimensions
Product Dimensions in Odoo
Dimensions
Website product dimensions
Odoo Website product dimensions
Website product dimensions in Odoo""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=wk_product_dimensions",
  "depends"              :  ['product'],
  "data"                 :  ['views/views.xml'],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "pre_init_hook"        :  "pre_init_check",
}
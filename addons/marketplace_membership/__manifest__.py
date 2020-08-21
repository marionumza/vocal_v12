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
  "name"                 :  "Odoo Marketplace Membership",
  "summary"              :  "Enable marketplace membership plan feature For your marketplace Sellers.",
  "category"             :  "Website",
  "version"              :  "1.0.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Marketplace-Membership.html",
  "description"          :  """https://webkul.com/blog/odoo-marketplace-membership/""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=marketplace_membership&lifetime=120&lout=1&custom_url=/",
  "depends"              :  ['odoo_marketplace'],
  "data"                 :  [
                             'security/marketplace_security.xml',
                             'security/ir.model.access.csv',
                             'data/mp_config_setting_data.xml',
                             'wizard/mp_membership_wizard_views.xml',
                             'views/mp_membership_view.xml',
                             'views/product_views.xml',
                             'views/res_partner_views.xml',
                             'views/website_config_view.xml',
                             'views/marketplace_config_view.xml',
                             'views/website_template_view.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  149,
  "currency"             :  "EUR",
  "pre_init_hook"        :  "pre_init_check",
}

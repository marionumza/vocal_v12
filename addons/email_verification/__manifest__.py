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
  "name"                 :  "Email Verification",
  "summary"              :  "The module sends email for verification on customer's email address while signing up to Odoo website. The customer needs to verify his email address to make purchase.",
  "category"             :  "Website",
  "version"              :  "3.0.8",
  "sequence"             :  10,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Website-Email-Verification.html",
  "description"          :  """Odoo Website Email Verification
Odoo Email Verification
Email authentication
Customer email verify link
Send mail verification link
Use email validation on Odoo website
Odoo mail verify
Odoo mail validation link
Verify email of customer
Email address verification
""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=email_verification",
  "depends"              :  [
                             'mail',
                             'website_webkul_addons',
                            ],
  "data"                 :  [
                             'data/email_template.xml',
                             'views/templates_view.xml',
                             'views/res_config_view.xml',
                             'views/res_users_view.xml',
                             'views/webkul_addons_config_inherit_view.xml',
                             'wizard/wizard_view.xml',
                            ],
  "demo"                 :  ['data/data.xml'],
  "images"               :  ['static/description/banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  29,
  "currency"             :  "EUR",
  "pre_init_hook"        :  "pre_init_check",
}
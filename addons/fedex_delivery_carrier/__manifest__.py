# -*- coding: utf-8 -*-
#################################################################################
##    Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    You should have received a copy of the License along with this program.
#    If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "FedEx Shipping Integration",
  "summary"              :  "Integrate Fedex shipping functionality directly within Odoo ERP applications to deliver increased logistical efficiencies.",
  "category"             :  "Website/Shipping Logistics",
  "version"              :  "1.1.2",
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "maintainer"           :  "Prakash Kumar",
  "website"              :  "https://store.webkul.com/Odoo-Website-Fedex-Shipping-Integration.html",
  "description"          :  """http://webkul.com/blog/odoo-fedex-shipping-integration/
  FedEx Shipping API Integration as Odoo FedEx Delivery Method .
  Provide Shipping Label Generation and Shipping Rate Calculator For Website as Well Odoo BackEnd.""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=fedex_delivery_carrier&version=12.0",
  "depends"              :  ['odoo_shipping_service_apps',
                              'website_sale_delivery',
                            ],
  "data"                 :  [
                             'data/data.xml',
                             'data/delivery_demo.xml',
                             'security/ir.model.access.csv',
                             'views/fedex_delivery_carrier.xml',
                             'views/product_packaging.xml',
                            ],
  "demo"                 :  ['data/demo.xml'],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "price"                :  149,
  "currency"             :  "EUR",
  "pre_init_hook"        :  "pre_init_check",
  "external_dependencies":  {'python': ['fedex']},
}

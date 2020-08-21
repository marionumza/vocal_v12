# -*- coding: utf-8 -*-
#################################################################################
##    Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    You should have received a copy of the License along with this program.
#    If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "DHL Shipping Integration",
  "summary"              :  "Integrate DHL shipping functionality directly within Odoo ERP applications to deliver increased logistical efficiencies.",
  "category"             :  "Website/Shipping Logistics",
  "version"              :  "0.1.2",
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo/Ecommerce-Website/Odoo-Website-DHL-Shipping-Integration.html",
  "description"          :  """https://webkul.com/blog/odoo-website-dhl-shipping-integration/
    DHL Shipping API Integration as Odoo DHL Delivery Method .
    Provide Shipping Label Generation and Shipping Rate Calculator For Website as Well Odoo BackEnd.""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=dhl_delivery_carrier&version=12.0",
  "depends"              :  ['odoo_shipping_service_apps',
                              'website_sale_delivery',
                            ],
  "data"                 :  [
                             'views/dhl_delivery_carrier.xml',
                             'security/ir.model.access.csv',
                             'data/data.xml',
                             'data/package.xml',
                             'data/delivery_demo.xml',
                            ],
  "demo"                 :  [
                             'data/demo.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "price"                :  149,
  "currency"             :  "EUR",
  "pre_init_hook"        :  "pre_init_check",
  "external_dependencies":  {'python': ['urllib3']},
}

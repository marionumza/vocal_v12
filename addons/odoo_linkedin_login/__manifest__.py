# -*- coding: utf-8 -*-

{
  "name"                 :  "Website LinkedIn Login/Sign-Up",
  "summary"              :  "When the user clicks on Login/Sign-Up, the requested form appears in a very nice Ajax popup, integrated with Facebook, Odoo, Google+, LinkedIn.",
  "category"             :  "Website",
  "version"              :  "1.0",
  "author"               :  "Krishnaram.S",
  "license"              :  "AGPL-3",
  "website"              :  "https://www.techversantinc.com",
  "depends"              :  [ 
                            'web',
                            'website',
                            'website_ajax_login',
                            'auth_oauth',
                            ],
  "data"                 :  [
                            'data/auth_data.xml',
                            'views/assets.xml',
                            'views/auth_view.xml',
                            ],
  "installable"          :  True,
  'auto_install'		     :  False,
}

# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class AmazonAffiliate(http.Controller):

    @http.route(['/amazon'], type='http', auth="public", website=True)
    def amazon_affiliate(self, redirect=None, **post):
        products = request.env['amazon.product'].search([])
        products_list = []
        product_dict = {}
        for product in products:
            product_dict['img_url'] = product.img_url
            product_dict['link_url'] = product.link_url
            products_list.append(product_dict)
        print("products_list==================", products_list)

        values = {
            'products': products_list
        }
        # values['img'] = "//ws-in.amazon-adsystem.com/widgets/q?_encoding=UTF8&MarketPlace=IN&ASIN=B083FLPNNL&ServiceVersion=20070822&ID=AsinImage&WS=1&Format=_SL250_&tag=vocal8866-21"
        # # values['url'] = "//ws-in.amazon-adsystem.com/widgets/q?ServiceVersion=20070822&OneJS=1&Operation=GetAdHtml&MarketPlace=IN&source=ac&ref=tf_til&ad_type=product_link&tracking_id=vocal8866-21&marketplace=amazon&region=IN&placement=B083FLPNNL&asins=B083FLPNNL&linkId=12e4c04ad675ca82ae0c0849b62a003c&show_border=false&link_opens_in_new_window=false&price_color=333333&title_color=0066C0&bg_color=FFFFFF"
        # values['a'] = "https://www.amazon.in/gp/product/B083FLPNNL/ref=as_li_tl?ie=UTF8&camp=3638&creative=24630&creativeASIN=B083FLPNNL&linkCode=as2&tag=vocal8866-21&linkId=4b54bce5bac29f6efffbe7b837c6ff85"
        return request.render("amazon_affiliate.amazon_product_template", values)

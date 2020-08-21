#  -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE URL <https://store.webkul.com/license.html/> for full copyright and licensing details.
#################################################################################
from odoo import http
from odoo.http import request
from odoo.tools.translate import _
from odoo.addons.website_sale.controllers.main import WebsiteSale
import logging
_logger = logging.getLogger(__name__)

class website_voucher(http.Controller):
	@http.route('/website/voucher/', type='json',  auth="public", methods=['POST'], website=True)
	def voucher_call(self, secret_code=False):
		try:
			result = {}
			voucher_obj = request.env['voucher.voucher']
			order= request.website.sale_get_order()
			wk_order_total = order.amount_total
			partner_id = request.env['res.users'].browse(request.uid).partner_id.id
			products =  []
			for line in order.order_line:
				products.append(line.product_id.id)
			result = voucher_obj.sudo().validate_voucher(secret_code, wk_order_total, products, refrence="ecommerce", partner_id=partner_id)
			if result['status']:
				final_result = request.website.sale_get_order(force_create=1)._add_voucher(wk_order_total, result)
				if not final_result['status']:
					result.update(final_result)
				request.session['secret_key_data'] = {'coupon_id':result['coupon_id'],'total_available':result['total_available'],'wk_voucher_value':result['value'],'voucher_val_type':result['voucher_val_type'],'customer_type':result['customer_type']}
			return result
		except Exception as e:
			_logger.info('-------------Exception-----%r',e)

	@http.route(['/shop/cart/voucher_remove/<line_id>'], type='http', auth="public",  website=True)
	def remove_voucher(self, line_id='0'):
		try:
			voucher_obj = request.env['voucher.voucher']
			product_id = request.env['ir.default'].sudo().get('res.config.settings', 'wk_coupon_product_id')
			secret_code = request.session.get('secret_key_data')
			if secret_code['total_available'] != -1:
				voucher_obj.sudo().return_voucher(secret_code['coupon_id'], int(line_id), refrence="ecommerce")
			if product_id and line_id:
				line_obj = request.env["sale.order.line"].sudo().browse(int(line_id))
				line_obj.sudo().unlink()
				request.session['secret_key_data'] = {}
			return request.redirect("/shop/cart/")
		except Exception as e:
			_logger.info('-------------Exception-----%r',e)
			return request.redirect("/shop/cart/")


	@http.route(['/voucher/validate/cart_change'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
	def cart_update_json(self):
		secret_data = request.session.get('secret_key_data')
		if secret_data.get('coupon_id'):
			order = request.website.sale_get_order(force_create=1)
			voucher_product_id = request.env['ir.default'].sudo().get('res.config.settings', 'wk_coupon_product_id')
			for line in order.order_line:
				if line.product_id.id == voucher_product_id:
					voucher_obj = request.env['voucher.voucher'].browse(secret_data.get('coupon_id'))
					if voucher_obj.use_minumum_cart_value and voucher_obj.minimum_cart_amount > order.amount_total:
						line.sudo().unlink()
						return True
					if order.amount_total == 0.0:
						line.sudo().unlink()
						return True
		return False
			
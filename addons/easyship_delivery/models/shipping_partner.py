import base64
import json
import requests
from odoo import tools
from odoo import models, fields, api
from odoo.modules.module import get_module_resource
from odoo.exceptions import UserError, Warning


class ShippingPartner(models.Model):
    _inherit = "shipping.partner"

    provider_company = fields.Selection(selection_add=[('easyship_ts', 'Easyship')])
    es_test_api_key = fields.Char("Test API Key", help="Enter your API test key from Easyship account.")
    es_production_api_key = fields.Char("Production API Key", help="Enter your API production key from Easyship account")

    @api.onchange('provider_company')
    def _onchange_provider_company(self):
        res = super(ShippingPartner, self)._onchange_provider_company()
        if self.provider_company == 'easyship_ts':
            image_path = get_module_resource('easyship_delivery', 'static/description', 'icon.png')
            self.image = tools.image_resize_image_big(base64.b64encode(open(image_path, 'rb').read()))
        return res

    def get_easyship_categ(self):
        category_obj = self.env['easyship.category']
        if self.provider_company == 'easyship_ts':
            response = self._easyship_send_request('reference/v1/categories', {}, prod_environment=True)
            categories = response.get('categories', [])
            for category in categories:
                existing = category_obj.search([('slug', '=', category.get('slug'))])
                if existing:
                    continue
                category_obj.create({'name': category.get('name'), 'slug': category.get('slug')})

    @api.model
    def _easyship_send_request(self, request_url, request_data, prod_environment=True, method='GET'):
        api_key = self.es_production_api_key if prod_environment else self.es_test_api_key
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % api_key
        }
        if request_data:
            data = json.dumps(request_data)
        else:
            data = False
        if prod_environment:
            api_url = 'https://api.easyship.com/' + request_url
        else:
            api_url = 'https://api-sandbox.easyship.com/' + request_url
        try:
            if data:
                req = requests.request(method, api_url, headers=headers, data=data)
            else:
                req = requests.request(method, api_url, headers=headers)
            req.raise_for_status()
            if isinstance(req.content, bytes):
                req = req.content.decode("utf-8")
                response = json.loads(req)
            else:
                response = json.loads(req.content)
        except requests.HTTPError as e:
            raise UserError("%s" % req.text)
        return response

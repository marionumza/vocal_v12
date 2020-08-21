import base64
import json
import requests
from odoo import tools
from odoo import models, fields, api
from odoo.modules.module import get_module_resource
from odoo.exceptions import UserError, Warning


class ShippingPartner(models.Model):
    _inherit = "shipping.partner"

    provider_company = fields.Selection(selection_add=[('easypost_ts', 'Easypost')])
    test_api_key = fields.Char("Test API Key", help="Enter your API test key from Easypost account.")
    production_api_key = fields.Char("Production API Key", help="Enter your API production key from Easypost account")

    @api.onchange('provider_company')
    def _onchange_provider_company(self):
        res = super(ShippingPartner, self)._onchange_provider_company()
        if self.provider_company == 'easypost_ts':
            image_path = get_module_resource('easypost_delivery', 'static/description', 'icon.png')
            self.image = tools.image_resize_image_big(base64.b64encode(open(image_path, 'rb').read()))
        return res

    def get_easypost_carriers(self):
        carrier_obj = self.env['easypost.carrier']
        if self.provider_company == 'easypost_ts' and self.production_api_key:
            carriers = self._easypost_send_request('carrier_accounts', {})
            for carrier in carriers:
                existing = carrier_obj.search([('easypost_id', '=', carrier.get('id'))])
                if existing:
                    continue
                carrier_obj.create({'easypost_id': carrier.get('id'), 'name': carrier.get('readable')})
        else:
            raise UserError('A production key is required to get your easypost carriers.')

    @api.model
    def _easypost_send_request(self, request_url, request_data, prod_environment=True, method='GET'):
        headers = {
            'Content-Type': 'application/json',
        }
        data = json.dumps(request_data)
        api_url = "https://api.easypost.com/v2/" + request_url
        api_key = self.production_api_key if prod_environment else self.test_api_key
        try:
            req = requests.request(method, api_url, auth=(api_key, ''), headers=headers, data=data)
            req.raise_for_status()
            if isinstance(req.content, bytes):
                req = req.content.decode("utf-8")
                response = json.loads(req)
            else:
                response = json.loads(req.content)
        except requests.HTTPError as e:
            raise Warning("%s" % req.text)
        return response

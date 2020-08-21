# -*- coding: utf-8 -*-
#################################################################################
##    Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    You should have received a copy of the License along with this program.
#    If not, see <https://store.webkul.com/license.html/>
#################################################################################
from odoo import api, fields , models

class WkShippingDhl(models.Model):
    _inherit="delivery.carrier"

    delivery_type = fields.Selection(
        selection_add = [('dhl','DHL')]
    )
    dhl_service_type = fields.Many2one(
        comodel_name = 'delivery.carrier.dhl.service',
        string = 'DHL Service'
    )
    dhl_drop_off_type = fields.Many2one(
        comodel_name = 'delivery.carrier.dhl.drop.off',
        string = 'DHL Drop-Off Type'
    )
    
    dhl_site_id = fields.Char(
         string ='Site ID',
         
    )
    dhl_account_no=fields.Char(
         string ='Account Number',
         
    )
    dhl_password =fields.Char(
         string ='Password',
         
    )

    @api.model
    def _get_config(self,key):
        if key=='dhl.config.settings':
            data  = self.read(['dhl_site_id','dhl_account_no','dhl_password','prod_environment'])[0]
            data['dhl_enviroment'] ='production' if data['prod_environment'] else  'test'  
            return data
        return super(ShippingFedex,self)._get_config(key)
    

class WK_ShippingDhlDropOff(models.Model):
    _name = "delivery.carrier.dhl.drop.off"

    name = fields.Char(
        string = "Name",
        required=1
    )
    code = fields.Char(
        string = "Code",
        required=1
    )


class WK_ShippingDhlService(models.Model):
    _name = "delivery.carrier.dhl.service"

    name = fields.Char(
        string = "Name",
        required=1
    )
    global_code = fields.Char(
        string = "Global Product Code",
        required=1
    )
    local_code = fields.Char(
        string = "Local Product Code",
        required=1
    )
    term_of_trade=fields.Char(
        string = "Terms Of Trade",
        required=1,
        default='DDU'
    )
    is_dutiable = fields.Selection(
        selection=[('N','No'),('Y','Yes')],
        string='IS Dutiable',
        required=1,
        default='N'
    )
    is_insured = fields.Selection(
        selection=[('N','No'),('Y','Yes')],
        string='IS Insured',
        required=1,
        default='N'
    )

class ProductPackage(models.Model):
    _inherit = 'product.package'

    delivery_type = fields.Selection(
        selection_add=[('dhl', 'DHL')]
    )
class ProductPackaging(models.Model):
    _inherit = 'product.packaging'

    package_carrier_type = fields.Selection(
        selection_add=[('dhl', 'DHL')]
    )
    dhl_ready_time = fields.Integer(
        string = "Ready Time",
        required=1,
        default=10,
        help='Package Ready Time after order submission(in hours)'
    )

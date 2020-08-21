# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2017-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    You should have received a copy of the License along with this program.
#    If not, see <https://store.webkul.com/license.html/>
#################################################################################

from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)
SIZE = [('REGULAR', 'Regular'), ('LARGE', 'Large')]
Boolean=[
    ('False','False'),
    ('True','True')
] 

HelpSize=_(
    """REGULAR: Package dimensions are 12 or less;\
                                    LARGE: Any package dimension is larger than 12."""
    )
HelpGrith=_("""[2 * (self.height + self.width)] Value must be numeric. Units are inches.
     Girth is only required when Container = ‘NONRECTANGULAR’ or decimal ‘VARIABLE’ and Size=’LARGE""")

HelpSignature=_("""No Signature Required for Delivery.
    Enter "true" if you do not want a  signature for receipt of the package""")

HelpMachinable=_("""Machinable is required when: ServiceType = 'ParcelPost'""")
 
HelpSeparateReceiptPage=_("""
    Label & Customer Online RecordPrinted on two separate pages.
    Enter "true" if you want the shipping label and online customer record printed on two separate
    pages or "false" if you want them printed on the same single page""")

class ProductPackage(models.Model):
    _inherit = 'product.package'

    @api.onchange('height', 'width')
    def _compute_grith(self):
        self.girth = 2 * (self.height + self.width)
    girth = fields.Integer(compute='_compute_grith', help=HelpGrith)


class ProductPackaging(models.Model):
    _inherit = 'product.packaging'
    @api.onchange('height', 'width')
    def _compute_grith(self):
        self.girth = 2 * (self.height + self.width)
    package_carrier_type = fields.Selection(selection_add=[('usps', 'USPS')])
    girth = fields.Integer(compute='_compute_grith')
    usps_machinable = fields.Selection(Boolean,default='False',help=HelpMachinable)
    usps_signature = fields.Selection( Boolean,string='Waiver Of Signature',default='True',help=HelpSignature)
    usps_package_size = fields.Selection(SIZE,default='REGULAR')

    @api.onchange('height', 'width')
    def _compute_grith(self):
        self.girth = 2 * (self.height + self.width)

class ShippingUSPS(models.Model):
    _inherit = "delivery.carrier"
    delivery_type = fields.Selection(selection_add=[('usps', 'USPS')])

    usps_servicetype = fields.Many2one(
        comodel_name='delivery.carrier.usps.service', string='Service Type')

class UspsService(models.Model):
    _name = "delivery.carrier.usps.service"
    name = fields.Char(string="Name",required=1)
    code = fields.Char(string="Code",required=1)

    usps_firstclassmailtype = fields.Many2one(
        comodel_name='delivery.carrier.usps.firstclassmailtype',
        string='USPS First Class Mail Type',
         help='Must be set When Using First Class Service')

class WK_ShippingUspsFirstclassmailtype(models.Model):
    _name = "delivery.carrier.usps.firstclassmailtype"
    name = fields.Char(string="Name",required=1)
    code = fields.Char(string="Code",required=1)

# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2017-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    You should have received a copy of the License along with this program.
#    If not, see <https://store.webkul.com/license.html/>
#################################################################################

import binascii
import logging
import requests
from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement
from xml.dom import minidom
from urllib.parse import  quote_plus
_logger = logging.getLogger(__name__)
try:
    from urllib3.exceptions import HTTPError
    import urllib3
except Exception as e:
    _logger.error("#WKDEBUG-1  python  urllib3 library not installed .")
from odoo import api, fields, models
from odoo.exceptions import ValidationError,UserError
from openerp.addons.odoo_shipping_service_apps.tools import ensure_str

headers = {"content-type":"text/xml"}
 
class USPSAPI:
    APIEND = dict(
            rate = 'http://production.shippingapis.com/ShippingAPI.dll?',
            shipping_test = 'https://stg-secure.shippingapis.com/ShippingAPI.dll?',
            shipping_production = "https://secure.shippingapis.com/ShippingAPI.dll?",
            tracking  = "https://tools.usps.com/go/TrackConfirmAction_input",
            cancel_test = "https://stg-secure.shippingapis.com/ShippingAPI.dll?",
            cancel_production = "https://secure.shippingapis.com/ShippingAPI.dll?" 
    )
    @staticmethod
    def check_error(root):
        error = False
        for Error in root.getiterator("Error"):
            error = True
        if error:
            message =  (','.join([i.text for i in root.getiterator("Description")]))
            _logger.info("%r===%r==="%(root.tag,message))
            return message

    @classmethod
    def get_tracking_link(cls,awb):
        return '%s?qtc_tLabels1=%s'%(cls.APIEND.get('tracking'),quote_plus(awb))

    @staticmethod
    def prettify(elem):
        rough_string = ElementTree.tostring(elem, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="\t")
    @staticmethod
    def add_text(elem, text):
        elem.text = text
        return elem

    def __init__(self, *args, **kwargs):
        self.usps_user_id = kwargs.get('usps_user_id')
        self.usps_currency = kwargs.get('usps_currency')
        self.usps_enviroment = kwargs.get('usps_enviroment','test')

    def send_request(self,request_for,request_xml):
        try:
            http = urllib3.PoolManager()
            api_end = self.APIEND.get(request_for)
            _logger.info("USPS api_end=%r=="%(api_end))
            response = requests.post(url = api_end,data = request_xml,headers = headers)
            root = ElementTree.fromstring(response.content)
            error = self.check_error(root)
            return dict(success = 0 if error else 1, error_message=error,root=root)
        except Exception as e:
            _logger.warning(
                "#WKDEBUG---USPS %r Exception-----%r---------"%(request_for,e))
            return dict(success = False, error_message=e)

    def contruct_dimension(self,root_node,data):
        width =data.get('width',1)
        length=data.get('length',1)
        height=data.get('height',1)
        girth =  data.get('girth') and data.get('girth') or 2*(width+height)
        self.add_text(SubElement(root_node, 'Container'),data.get('shipper_package_code'))
        self.add_text(SubElement(root_node, 'Size'),data.get('usps_package_size'))
        self.add_text(SubElement(root_node, 'Width'),'%s'%width)
        self.add_text(SubElement(root_node, 'Length'),'%s'%length)
        self.add_text(SubElement(root_node, 'Height'),'%s'%height)
        self.add_text(SubElement(root_node, 'Machinable'),data.get('usps_machinable'))

        return root_node

    def contruct_dimension_ship(self,root_node,data):
        width =data.get('width',1)
        length=data.get('length',1)
        height=data.get('height',1)
        girth =  data.get('girth') and data.get('girth') or 2*(width+height)
        self.add_text(SubElement(root_node, 'Container'),data.get('shipper_package_code'))
        self.add_text(SubElement(root_node, 'Width'),'%s'%width)
        self.add_text(SubElement(root_node, 'Length'),'%s'%length)
        self.add_text(SubElement(root_node, 'Height'),'%s'%height)
        self.add_text(SubElement(root_node, 'Machinable'),data.get('usps_machinable'))

        return root_node

    def contruct_req_package(self,data):
        Package = Element('Package',attrib={'ID': '%s'%data.get('index',1)})
        self.add_text(SubElement(Package, 'Service'),data.get('usps_service_code'))
        if data.get('usps_service_code')=='FIRST CLASS':
                self.add_text(SubElement(Package, 'FirstClassMailType'),data.get('usps_firstclassmailtype'))
        self.add_text(SubElement(Package, 'ZipOrigination'),data.get('zip_origin'))
        self.add_text(SubElement(Package, 'ZipDestination'),data.get('zip_destination'))
        self.add_text(SubElement(Package, 'Pounds'),'0')
        self.add_text(SubElement(Package, 'Ounces'),'%s'%data.get('weight'))
        self.contruct_dimension(Package,data)
        self.add_text(SubElement(Package, 'ReturnLocations'),False)
        return Package

    def contruct_rate_request(self,packages):
        Request = Element("RateV4Request",attrib={'USERID':self.usps_user_id})
        for package in packages:
            Request.append(package)
        return Request

    def send_rate_request(self,data):
        response = self.send_request('rate','API=RateV4&XML=%s'%data)  
        if response.get('error_message'):return response
        root = response.get('root')
        price = 0
        for rate in root.iter('Rate'):
            price += float(rate.text)
        return dict(price = price, currency=None,success=True)

    def construct_ship_address(self,root_node,attr,data):
        self.add_text(SubElement(root_node, '%sName'%attr),data.get('name'))
        if data.get('company_name'):
            self.add_text(SubElement(root_node, '%sFirm'%attr),data.get('company_name'))
        self.add_text(SubElement(root_node, '%sAddress1'%attr),data.get('street'))
        self.add_text(SubElement(root_node, '%sAddress2'%attr),data.get('street2') or '. ')
        self.add_text(SubElement(root_node, '%sCity'%attr),data.get('city'))
        self.add_text(SubElement(root_node, '%sState'%attr),data.get('state_code'))
        self.add_text(SubElement(root_node, '%sZip5'%attr),data.get('zip'))
        SubElement(root_node, '%sZip4'%attr)
        return root_node

    @api.model
    def construct_ship_sender_recept(self,root_node,attr,data):
        self.add_text(SubElement(root_node, '%sName'%attr),data.get('name'))
        self.add_text(SubElement(root_node, '%sEMail'%attr),data.get('email'))
        return root_node

    def get_shipment_api(self):
        return "eVSCertify" if self.usps_enviroment== 'test' else 'eVS'

    def get_cancel_api(self):
        return "eVSCancel"

    def contruct_ship_request(self,data,shipper_data,recipient_data):
        node = self.get_shipment_api()
        Request = Element("%sRequest"%node,attrib={'USERID':self.usps_user_id})
        self.add_text(SubElement(Request, 'Option'),'1')
        self.add_text(SubElement(Request, 'Revision'),'2')
        ImageParameters = SubElement(Request, 'ImageParameters')
        if data.get('number_of_packages')>1:
            LabelSequence = SubElement(ImageParameters, 'LabelSequence')
            self.add_text(SubElement(LabelSequence, 'PackageNumber'),'%s'%data.get('index'))
            self.add_text(SubElement(LabelSequence, 'TotalPackages'),'%s'%data.get('number_of_packages'))

        self.construct_ship_address(Request,'From',shipper_data)
        self.add_text(SubElement(Request,'FromPhone'),'%s'%shipper_data.get('phone'))
        self.construct_ship_address(Request,'To',recipient_data)
        self.add_text(SubElement(Request,'ToPhone'),'%s'%recipient_data.get('phone'))

        if recipient_data.get('email'):
            self.add_text(SubElement(Request, 'ToContactPreference'),'EMAIL')
            self.add_text(SubElement(Request, 'ToContactEMail'),'%s'%recipient_data.get('email'))
        elif recipient_data.get('phone'):
            self.add_text(SubElement(Request, 'ToContactPreference'),'SMS')
            self.add_text(SubElement(Request, 'ToContactMessaging'),'%s'%recipient_data.get('phone'))

        self.add_text(SubElement(Request, 'AllowNonCleansedDestAddr'),'True')
        self.add_text(SubElement(Request, 'WeightInOunces'),'%s'%data.get('weight'))
        self.add_text(SubElement(Request, 'ServiceType'),'%s'%data.get('usps_servicetype'))
        self.contruct_dimension_ship(Request,data)
        self.add_text(SubElement(Request, 'CustomerRefNo'),data.get('reference'))
        self.construct_ship_sender_recept(Request,'Sender',shipper_data)
        self.construct_ship_sender_recept(Request,'Recipient',recipient_data)
        self.add_text(SubElement(Request, 'ImageType'),'tif')
        self.add_text(SubElement(Request, 'HoldForManifest'),'N')
        self.add_text(SubElement(Request, 'ReturnCommitments'),'true')
        return Request


    def send_ship_request(self,xml_data):
        node = self.get_shipment_api()
        if node == "eVSCertify":
            response = self.send_request('shipping_test','API=%s&XML=%s'%(node,xml_data))
        else:
            response = self.send_request('shipping_production','API=%s&XML=%s'%(node,xml_data))

        if response.get('error_message'):return response
        root = response.get('root')
        tracking_result = dict()
        date_delivery = root.find('Commitment').findtext('ScheduledDeliveryDate')
        for tracking_number, image in zip(root.getiterator("BarcodeNumber"), root.getiterator("LabelImage")):
            tracking_result[tracking_number.text]= ('USPS' + str(tracking_number.text) + '.tif', binascii.a2b_base64(image.text))
        return dict(tracking_result=tracking_result,date_delivery=date_delivery)


    def construct_cancel_request(self,tracking_link):
        node = self.get_cancel_api()
        Request = Element("%sRequest"%node,attrib={'USERID':self.usps_user_id})
        self.add_text(SubElement(Request, 'BarcodeNumber'),tracking_link)
        return Request

    def send_cancel_request(self,xml_data):
        node = self.get_cancel_api()
        if self.usps_enviroment == "test":
            response = self.send_request('cancel_test','API=%s&XML=%s'%(node,xml_data))
        else:
            response = self.send_request('cancel_production','API=%s&XML=%s'%(node,xml_data))
        return response

class UspsDeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    usps_user_id=fields.Char(string="User ID")
    
    @api.model
    def get_usps_packages(self,sdk, order=None):
        result =[]
        packaging_obj = self.env['product.packaging']
        recipient = order.partner_shipping_id if order.partner_shipping_id else order.partner_id
        shipper = order.warehouse_id.partner_id
        package_items = self.wk_get_order_package(order=order)
        items=self.wk_group_by('packaging_id',package_items)
        service = self.usps_servicetype
        for order_packaging_id, wk_package_ids in items:
            packaging_id = packaging_obj.browse(order_packaging_id)
            packaging_data = packaging_id.read(['shipper_package_code','usps_package_size','usps_machinable'])[0]
            packaging_data.pop('id')
            for index,package_id in enumerate(wk_package_ids,1):
                data =dict(
                    index = index,
                    weight  =package_id.get('weight'),
                    usps_service_code = service.code,
                    usps_firstclassmailtype = service.usps_firstclassmailtype.code,
                    zip_origin = shipper.zip,
                    zip_destination = recipient.zip,
                )
                data.update(packaging_data)
                result.append(sdk.contruct_req_package(data))
        return result

    @api.model
    def usps_get_shipping_price(self, order):
        recipient = order.partner_shipping_id if order.partner_shipping_id else order.partner_id
        shipper = order.warehouse_id.partner_id
        currency_id = self.get_shipment_currency_id(order)
        currency_code = currency_id.name
        price = 0
        config = self.wk_get_carrier_settings(['usps_user_id','prod_environment'])
        if config['prod_environment']:
            config['usps_enviroment'] = 'production'
        config['usps_currency'] = currency_code
        sdk = USPSAPI(**config)
        config = self.wk_get_carrier_settings(['usps_user_id','prod_environment'])
        if config['prod_environment']:
            config['usps_enviroment'] = 'production'
        packages =self.get_usps_packages(sdk,order=order)
        rate_req = sdk.contruct_rate_request(packages)
        rate_req_xml = sdk.prettify(rate_req)
        response = sdk.send_rate_request(rate_req_xml)
        response['currency'] = currency_code
        response['currency_id'] =currency_id
        return response

    @api.model
    def usps_rate_shipment(self, order):
        response = self.usps_get_shipping_price(order)
        if not response.get('error_message'):response['error_message'] = None
        if not response.get('price'):response['price'] = 0
        if not response.get('warning_message'):response['warning_message'] = None
        if not response.get('success'):return response
        price = self.convert_shipment_price(response)
        response['price'] = price
        return response

    @api.one
    def usps_send_shipping(self, pickings):
        self.wk_validate_data(pickings=pickings)
        result = {'exact_price': 0, 'weight': 0, "date_delivery": None,
                  'tracking_number': '', 'attachments': []}
        currency_id = self.get_shipment_currency_id(pickings=pickings)
        currency_code = currency_id.name
        total_package = 0
        shipper_info = self.get_shipment_shipper_address(picking=pickings)
        shipper_info['company_name'] = pickings.company_id and pickings.company_id.name or ""
        recipient_info  = self.get_shipment_recipient_address(picking=pickings)
        recipient_info['company_name'] = pickings.company_id and pickings.company_id.name or ""
        config = self.wk_get_carrier_settings(['usps_user_id','prod_environment'])
        config['usps_currency'] = currency_code
        if config['prod_environment']:
            config['usps_enviroment'] = 'production'
        sdk = USPSAPI(**config)
        package_ids = pickings.package_ids
        service = self.usps_servicetype.code
        reference =  pickings.origin
        number_of_packages =  len(pickings.package_ids)
        tracking_numbers = []
        for index,package_id in enumerate(package_ids,1):
            weight=self._get_api_weight(package_id.shipping_weight) or (self.default_product_weight)
            pkg_data = package_id.packaging_id.read(['height', 'width','length','cover_amount','shipper_package_code',
            'usps_package_size','usps_machinable','usps_signature'])[0]
            ship_data = dict(
                weight =weight,
                index = index,
                number_of_packages =number_of_packages,
                usps_servicetype =service,
                reference = reference,
            )
            ship_data.update(pkg_data)
            ship_request = sdk.contruct_ship_request(ship_data,shipper_info,recipient_info)
            ship_req_xml = sdk.prettify(ship_request)
            response = sdk.send_ship_request(ship_req_xml)
            if response.get('error_message'):
                raise ValidationError(response.get('error_message'))
            tracking_result = response.get('tracking_result')
            tracking_numbers+=tracking_result.keys()
            result['weight'] += weight
            if tracking_result:
                result['attachments'] += list(tracking_result.values())
        result['tracking_number'] += ','.join(tracking_numbers)
        pickings.number_of_packages= number_of_packages
        return result

    @api.model
    def usps_get_tracking_link(self, pickings):
        return USPSAPI.get_tracking_link(pickings.carrier_tracking_ref)

    @api.model
    def usps_cancel_shipment(self, pickings):
        currency_id = self.get_shipment_currency_id(pickings=pickings)
        currency_code = currency_id.name
        config = self.wk_get_carrier_settings(['usps_user_id','prod_environment'])
        config['usps_currency'] = currency_code
        if config['prod_environment']:
            config['usps_enviroment'] = 'production'
        sdk = USPSAPI(**config)
        tracking_link = pickings.carrier_tracking_ref
        cancel_request = sdk.construct_cancel_request(tracking_link)
        cancel_req_xml = sdk.prettify(cancel_request)
        response = sdk.send_cancel_request(cancel_req_xml)
        if response:
            if response['success']:
                if response['root'].findtext('Status') == "Not Cancelled":
                    raise UserError("Shipment Cancellation Error:\n\nMessage: {}".format(response['root'].findtext('Reason')))
            else :
                raise UserError(response['error_message'])
        else:
            raise UserError("Could not fetch response. Please check your request data !!!")
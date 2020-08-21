# -*- coding: utf-8 -*-
#################################################################################
##    Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    You should have received a copy of the License along with this program.
#    If not, see <https://store.webkul.com/license.html/>
#################################################################################
import binascii
import logging
from datetime import datetime
import xml.etree.ElementTree as etree
from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement
from xml.etree.ElementTree import dump
from xml.dom import minidom
from urllib.parse import  quote_plus
# https://github.com/alfallouji/DHL-API
_logger = logging.getLogger(__name__)
try:
    from urllib3.exceptions import HTTPError
    import urllib3
except Exception as e:
    _logger.error("#WKDEBUG-1  python  urllib3 library not installed .")

from odoo import api, fields , models
from odoo.exceptions import ValidationError

class DHLAPI:
    APIEND = dict(
            test = 'https://xmlpitest-ea.dhl.com/XMLShippingServlet',
            production = 'https://xmlpi-ea.dhl.com/XMLShippingServlet',
            tracking  = "http://www.dhl.com/en/express/tracking.html"
    )
    @staticmethod
    def check_error(root):
        error = False
        ConditionData = root.getiterator("ConditionData")
        for ConditionCode in root.getiterator("ConditionCode"):
            if ConditionCode.text not in ['DIV001','SV009'] :
                error = True
        if error:return (','.join([i.text for i in root.getiterator("ConditionData")]))

    @classmethod
    def get_tracking_link(cls,awb):
        return '%s?AWB=%s'%(cls.APIEND.get('tracking'),quote_plus(awb))

    @staticmethod
    def get_message_time():
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%S GMT")

    @staticmethod
    def add_text(elem, text):
        elem.text = text
        return elem

    @staticmethod
    def prettify(elem):
        rough_string = ElementTree.tostring(elem, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="\t")

    def __init__(self, *args, **kwargs):
        self.dhl_site_id = kwargs.get('dhl_site_id')
        self.dhl_password = kwargs.get('dhl_password')
        self.dhl_account_no = kwargs.get('dhl_account_no')
        self.dhl_currency = kwargs.get('dhl_currency')
        self.dhl_enviroment = kwargs.get('dhl_enviroment','test')

    def send_request(self,request_xml):
        try:
            http = urllib3.PoolManager()
            api_end = self.APIEND.get(self.dhl_enviroment or 'test')
            _logger.info("DHL api_end=%r=="%(api_end))
            response = http.urlopen('POST',api_end, body=request_xml)
            root = etree.fromstring(response.data)
            error = self.check_error(root)
            return dict(success = 0 if error else 1, error_message=error,root=root)
        except Exception as e:
            _logger.warning(
                "#WKDEBUG---DHL %r Exception-----%r---------"%(request_xml,e))
            return dict(success = False, error_message=e)

    def contruct_request(self):
        Request = Element("Request")
        ServiceHeader = SubElement(Request, 'ServiceHeader')
        self.add_text(SubElement(ServiceHeader, 'MessageTime'),self.get_message_time())
        self.add_text(SubElement(ServiceHeader, 'MessageReference'),'1234567890123456789012345678901')
        self.add_text(SubElement(ServiceHeader, 'SiteID'),self.dhl_site_id)
        self.add_text(SubElement(ServiceHeader, 'Password'),self.dhl_password)
        return Request

    def contruct_piece(self,data,pickings=False):
        Piece = Element("Piece")
        if data.get('piece_id'):
                self.add_text(SubElement(Piece, 'PieceID'),'%s'%data.get('piece_id'))

        if not pickings:
            # if data.get('shipper_package_code'):
            #     self.add_text(SubElement(Piece, 'PackageTypeCode'),data.get('shipper_package_code'))
            self.add_text(SubElement(Piece, 'Height'),'%s'%int(round(data.get('height'))))
            self.add_text(SubElement(Piece, 'Depth'),'%s'%int(round(data.get('depth'))))
            self.add_text(SubElement(Piece, 'Width'),'%s'%int(round(data.get('width'))))
            self.add_text(SubElement(Piece, 'Weight'),'%s'%data.get('weight'))
        else:
            if data.get('shipper_package_code'):
                self.add_text(SubElement(Piece, 'PackageType'),data.get('shipper_package_code'))
            self.add_text(SubElement(Piece, 'Weight'),'%s'%data.get('weight'))
            self.add_text(SubElement(Piece, 'Depth'),'%s'%int(round(data.get('depth'))))
            self.add_text(SubElement(Piece, 'Width'),'%s'%int(round(data.get('width'))))
            self.add_text(SubElement(Piece, 'Height'),'%s'%int(round(data.get('height'))))
        return Piece

    def contruct_dutiable(self,data,picking=False):
        Dutiable = Element('Dutiable')
        if not picking:
            self.add_text(SubElement(Dutiable, 'DeclaredCurrency'),self.dhl_currency)
            self.add_text(SubElement(Dutiable, 'DeclaredValue'),'%.2f'%data.get('declared_value'))
        else:
            self.add_text(SubElement(Dutiable, 'DeclaredValue'),'%.2f'%data.get('declared_value'))
            self.add_text(SubElement(Dutiable, 'DeclaredCurrency'),self.dhl_currency)
            if data.get('term_of_trade'):
                self.add_text(SubElement(Dutiable, 'TermsOfTrade'),data.get('term_of_trade'))
        return Dutiable

    def contruct_quote_addrs(self,addr_type,data):
        Address = Element(addr_type)
        self.add_text(SubElement(Address, 'CountryCode'),data.get('country_code'))
        self.add_text(SubElement(Address, 'Postalcode'),data.get('zip'))
        return Address

    def contruct_bkg_details(self,data, shipper_data,pieces):
        BkgDetails = Element('BkgDetails')
        self.add_text(SubElement(BkgDetails, 'PaymentCountryCode'),shipper_data.get('country_code'))
        self.add_text(SubElement(BkgDetails, 'Date'),data.get('ship_date'))
        self.add_text(SubElement(BkgDetails, 'ReadyTime'),data.get('ready_time'))

        self.add_text(SubElement(BkgDetails, 'DimensionUnit'),data.get('dimension_unit'))
        self.add_text(SubElement(BkgDetails, 'WeightUnit'),data.get('weight_unit'))
        BkgDetails.append(pieces)
        self.add_text(SubElement(BkgDetails, 'IsDutiable'),data.get('is_dutiable'))
        self.add_text(SubElement(BkgDetails, 'NetworkTypeCode'),'AL')

        QtdShp = SubElement(BkgDetails, 'QtdShp')
        self.add_text(SubElement(QtdShp, 'GlobalProductCode'),data.get('global_code'))
        self.add_text(SubElement(QtdShp, 'LocalProductCode'),data.get('local_code'))
        if data.get('term_of_trade')=='DDP':
            QtdShpExChrg =  SubElement(QtdShp, 'QtdShpExChrg')
            self.add_text(SubElement(QtdShpExChrg, 'SpecialServiceType'),'DD')
        if data.get('is_insured')=='Y':
            QtdShpExChrg =  SubElement(QtdShp, 'QtdShpExChrg')
            self.add_text(SubElement(QtdShpExChrg, 'SpecialServiceType'),'II')
            self.add_text(SubElement(QtdShpExChrg, 'ChargeValue'),data.get('declared_value'))
            self.add_text(SubElement(QtdShpExChrg, 'CurrencyCode'),self.dhl_currency)
        return BkgDetails

    def dhl_construct_rate_request(self,data,shipper_data,recipient_data,pieces):
        attrib={
            "xmlns:p": "http://www.dhl.com",
            "xmlns:p1":"http://www.dhl.com/datatypes",
            "xmlns:p2":"http://www.dhl.com/DCTRequestdatatypes",
            "xmlns:xsi":"http://www.w3.org/2001/XMLSchema-instance",
            "xsi:schemaLocation":"http://www.dhl.com DCT-req.xsd",
        }
        DCTRequest = Element('p:DCTRequest',attrib=attrib)
        GetQuote = SubElement(DCTRequest, 'GetQuote')
        GetQuote.append(self.contruct_request())
        GetQuote.append(self.contruct_quote_addrs('From',shipper_data))
        GetQuote.append(self.contruct_bkg_details(data,shipper_data,pieces))
        GetQuote.append(self.contruct_quote_addrs('To',recipient_data))
        if data.get('is_dutiable')!='N':
            GetQuote.append(self.contruct_dutiable(data))
        return DCTRequest


    def send_rate_request(self,data):
        response = self.send_request(data)
        if response.get('error_message'):return response
        root = response.get('root')
        price = 0
        currency  = None
        ShippingCharge = list(root.iterfind('GetQuoteResponse/BkgDetails/QtdShp/ShippingCharge'))
        CurrencyCode = list(root.iterfind('GetQuoteResponse/BkgDetails/QtdShp/CurrencyCode'))
        if len(ShippingCharge):price = float(ShippingCharge[0].text)
        if len(CurrencyCode):currency = CurrencyCode[0].text
        return dict(price = price, currency=currency,success=True)


    def contruct_ship_addrs(self,addr_type,data):
        "addr_type==>Consignee,Shipper"
        AddressRoot =  Element(addr_type)
        if addr_type=='Shipper':
            self.add_text(SubElement(AddressRoot, 'ShipperID'),self.dhl_account_no)
        self.add_text(SubElement(AddressRoot, 'CompanyName'),data.get('name'))
        self.add_text(SubElement(AddressRoot, 'AddressLine'),data.get('street'))
        # self.add_text(SubElement(AddressRoot, 'AddressLine1'),data.get('street2'))
        self.add_text(SubElement(AddressRoot, 'City'),data.get('city'))
        self.add_text(SubElement(AddressRoot, 'PostalCode'),data.get('zip'))
        self.add_text(SubElement(AddressRoot, 'CountryCode'),data.get('country_code'))
        self.add_text(SubElement(AddressRoot, 'CountryName'),data.get('country_name'))
        Contact = SubElement(AddressRoot, 'Contact')
        self.add_text(SubElement(Contact, 'PersonName'),data.get('name'))
        self.add_text(SubElement(Contact, 'PhoneNumber'),data.get('phone'))
        return AddressRoot

    def contruct_shipment_details(self,data,pieces):
        ShipmentDetails = Element('ShipmentDetails')
        self.add_text(SubElement(ShipmentDetails, 'NumberOfPieces'),'%s'%data.get('number_of_pieces'))
        self.add_text(SubElement(ShipmentDetails, 'CurrencyCode'),self.dhl_currency)
        ShipmentDetails.append(pieces)
        self.add_text(SubElement(ShipmentDetails, 'PackageType'),data.get('shipper_package_code'))
        self.add_text(SubElement(ShipmentDetails, 'Weight'),'%s'%data.get('weight'))
        self.add_text(SubElement(ShipmentDetails, 'DimensionUnit'),data.get('dimension_unit'))
        self.add_text(SubElement(ShipmentDetails, 'WeightUnit'),data.get('weight_unit'))
        self.add_text(SubElement(ShipmentDetails, 'GlobalProductCode'),data.get('global_code'))
        self.add_text(SubElement(ShipmentDetails, 'LocalProductCode'),data.get('local_code'))
        self.add_text(SubElement(ShipmentDetails, 'DoorTo'),data.get('drop_off_type'))
        self.add_text(SubElement(ShipmentDetails, 'Date'),data.get('ship_date'))
        self.add_text(SubElement(ShipmentDetails, 'Contents'),data.get('contents'))
        if data.get('is_insured')=='Y':
            self.add_text(SubElement(ShipmentDetails, 'InsuredAmount'),'%.2f'%data.get('declared_value'))
        else:
            self.add_text(SubElement(ShipmentDetails, 'IsDutiable'),data.get('is_dutiable'))
        # self.add_text(SubElement(ShipmentDetails, 'CustData'),'Customer information to be printed on the label')

        return ShipmentDetails

    def dhl_construct_ship_request(self,data,shipper_data,recipient_data,pieces):
        attrib={
            "xmlns:p": "http://www.dhl.com",
            "xmlns:p1":"http://www.dhl.com/datatypes",
            "xmlns:p2":"http://www.dhl.com/DCTRequestdatatypes",
            "xmlns:xsi":"http://www.w3.org/2001/XMLSchema-instance",
            "xsi:schemaLocation":"http://www.dhl.com ship-val-req_EA.xsd",
        }
        RequestEA = Element('p:ShipmentValidateRequestEA',attrib=attrib)
        RequestEA.append(self.contruct_request())
        self.add_text(SubElement(RequestEA, 'LanguageCode'),shipper_data.get('lang'))
        self.add_text(SubElement(RequestEA, 'PiecesEnabled'),'Y')

        Billing = Element('Billing')
        self.add_text(SubElement(Billing, 'ShipperAccountNumber'),self.dhl_account_no)
        self.add_text(SubElement(Billing, 'ShippingPaymentType'),'S')
        if  data.get('term_of_trade')=='DDP':
            # self.add_text(SubElement(Billing, 'BillingAccountNumber'),self.dhl_account_no)
            self.add_text(SubElement(Billing, 'DutyPaymentType'),'S')
            self.add_text(SubElement(Billing, 'DutyAccountNumber'),self.dhl_account_no)
        RequestEA.append(Billing)

        RequestEA.append(self.contruct_ship_addrs('Consignee',recipient_data))
        if data.get('is_dutiable')!='N':
            RequestEA.append(self.contruct_dutiable(data,True))

        Reference = Element('Reference')
        self.add_text(SubElement(Reference, 'ReferenceID'),data.get('reference'))
        RequestEA.append(Reference)
        RequestEA.append(self.contruct_shipment_details(data,pieces))
        RequestEA.append(self.contruct_ship_addrs('Shipper',shipper_data))
        if data.get('term_of_trade')=='DDP':
            SpecialService = SubElement(RequestEA, 'SpecialService')
            self.add_text(SubElement(SpecialService, 'SpecialServiceType'),'DD')
        if data.get('is_insured')=='Y':
            SpecialService = SubElement(RequestEA, 'SpecialService')
            self.add_text(SubElement(SpecialService, 'SpecialServiceType'),'II')
            self.add_text(SubElement(SpecialService, 'ChargeValue'),'%.2f'%data.get('declared_value'))
            self.add_text(SubElement(SpecialService, 'CurrencyCode'),self.dhl_currency)
        self.add_text(SubElement(RequestEA, 'LabelImageFormat'),'PDF')
        return RequestEA

    def send_shipment_request(self,data):
        response = self.send_request(data)
        if response.get('error_message'):return response
        root = response.get('root')
        currency = 'USD'
        amount  =root.findtext('ShippingCharge')
        tracking_result = dict()
        for tracking_number, image in zip(root.getiterator("AirwayBillNumber"), root.getiterator("OutputImage")):
            tracking_result[tracking_number.text]= ('DHL' + str(tracking_number.text) + '.pdf', binascii.a2b_base64(image.text))
        return dict(currency =currency , amount =amount,
            tracking_result=tracking_result
        )

class DhlDeliveryCarrier(models.Model):
    _inherit="delivery.carrier"
    @api.model
    def dhl_get_shipping_price_piece(self,sdk,order):
        pass

    @api.model
    def dhl_get_shipping_data(self,order=None,pickings=None):
        res = self.dhl_service_type.read(['is_dutiable','is_insured','global_code','local_code','term_of_trade'])[0]
        res.pop('id')
        if order:
            res.update(dict(
                ship_date=fields.Datetime.from_string(order.date_order).strftime("%Y-%m-%d"),
                dimension_unit = (self.delivery_uom =='KG') and 'CM' or 'IN',
                weight_unit = (self.delivery_uom =='KG') and 'KG' or 'LB',
                reference = order.name or order.origin,
            ))
        else:
            contents='Customer Order %s'%pickings.name
            if pickings.origin: contents = 'Customer Order Reference '+pickings.origin
            res.update(dict(
                ship_date=fields.Datetime.from_string(pickings.scheduled_date).strftime("%Y-%m-%d"),
                dimension_unit = (self.delivery_uom =='KG') and 'C' or 'I',
                weight_unit = (self.delivery_uom =='KG') and 'K' or 'L',
                reference = pickings.origin or pickings.name,
                drop_off_type = self.dhl_drop_off_type.code,
                contents = contents,
            ))

        return res

    @api.model
    def dhl_get_shipping_price(self,order):
        Packaging = self.env['product.packaging']
        currency_id = self.get_shipment_currency_id(order)
        currency_code = currency_id.name
        shipper_info = self.get_shipment_shipper_address(order)
        recipient_info  = self.get_shipment_recipient_address(order)
        data =self.dhl_get_shipping_data(order)
        config = self._get_config('dhl.config.settings')
        config['dhl_currency'] = currency_code
        sdk = DHLAPI(**config)

        package_items = self.wk_get_order_package(order=order)
        items = self.wk_group_by('packaging_id', package_items)
        result = dict()
        tot_price = 0
        index=1
        for order_packaging_id, wk_package_ids in items:
            packaging_id = Packaging.browse(order_packaging_id)
            wk_cover_amount = sum(map(lambda i:i.get('wk_cover_amount',0),wk_package_ids))
            declared_value = packaging_id.get_cover_amount(wk_cover_amount) or 0
            pieces = Element('Pieces')
            for package_id in wk_package_ids:
                weight = self._get_api_weight(package_id.get('weight'))
                weight = weight and weight or self.default_product_weight
                piece_data = dict(
                    piece_id=index,
                    height=package_id.get('height'),
                    depth=package_id.get('width'),
                    width=package_id.get('length'),
                    weight=weight,
                )
                pieces.append(sdk.contruct_piece(piece_data))
                index+=1
            data['ready_time'] ='PT%sH00M'%(packaging_id.dhl_ready_time)
            data['declared_value'] =declared_value

            rate_req = sdk.dhl_construct_rate_request(
            data,shipper_info,recipient_info,pieces)
            rate_req_xml = sdk.prettify(rate_req)
            response = sdk.send_rate_request(rate_req_xml)
            _logger.info("###===%r===="%(response))
            if response.get('error_message'):
                return response
            else:
                tot_price+=response.get('price')
                result['currency'] = response.get('price')
        result['success'] =True
        result['price'] = tot_price
        result['currency_id'] =currency_id
        _logger.info("===%r===="%(result))
        return result

    @api.model
    def dhl_rate_shipment(self, order):
       response = self.dhl_get_shipping_price(order)
       _logger.info("##########11order===%r==%r=="%(order,response))
       if not response.get('error_message'):response['error_message'] = None
       if not response.get('price'):response['price'] = 0
       if not response.get('warning_message'):response['warning_message'] = None
       if not response.get('success'):return response
       price = self.convert_shipment_price(response)
       response['price'] = price
       _logger.info("##########22order===%r==%r=="%(order,response))
       return response

    @api.one
    def dhl_send_shipping(self,pickings):
        result = {
            'exact_price': 0,
            'weight': 0,
            'date_delivery': None,
            'tracking_number': '',
            'attachments': []
        }
        currency_id = self.get_shipment_currency_id(pickings=pickings)
        currency_code = currency_id.name
        total_package = 0
        shipper_info = self.get_shipment_shipper_address(picking=pickings)
        recipient_info  = self.get_shipment_recipient_address(picking=pickings)

        config = self._get_config('dhl.config.settings')
        config['dhl_currency'] = currency_code
        sdk = DHLAPI(**config)
        packaging_ids = self.wk_group_by_packaging(pickings=pickings)
        for packaging_id, package_ids in packaging_ids.items():
            declared_value = sum(map(lambda i:i.cover_amount,package_ids))
            weight_value = 0
            index = 1
            pkg_data = packaging_id.read(['height', 'width', 'length','shipper_package_code'])[0]
            _logger.info("==+%r=%r==%r==="%(pkg_data,packaging_id,declared_value))
            number_of_packages =  len(package_ids)
            total_package += number_of_packages
            pieces = Element('Pieces')
            for package_id in package_ids:
                weight = self._get_api_weight(package_id.shipping_weight)
                weight = weight and weight or self.default_product_weight

                weight_value+=weight
                piece_data = dict(
                    piece_id=index,
                    weight=weight,
                    height=pkg_data.get('height'),
                    depth=pkg_data.get('width'),
                    width=pkg_data.get('length'),
                    shipper_package_code=pkg_data.get('shipper_package_code')

                )
                pieces.append(sdk.contruct_piece(piece_data,pickings=pickings))
                index+=1

            data =self.dhl_get_shipping_data(pickings=pickings)
            data['weight'] = weight_value
            data['declared_value'] =declared_value
            data['number_of_pieces'] = index-1
            data['shipper_package_code'] =pkg_data.get('shipper_package_code')
            ship_req = sdk.dhl_construct_ship_request(
            data,shipper_info,recipient_info,pieces)
            ship_req_xml = sdk.prettify(ship_req)
            response = sdk.send_shipment_request(ship_req_xml)
            if response.get('error_message'):
                raise ValidationError(response.get('error_message'))
            tracking_result = response.get('tracking_result')
            result['weight'] += weight_value
            if tracking_result:
                result['tracking_number'] += ','.join(tracking_result.keys())
                result['attachments'] += list(tracking_result.values())
        _logger.info("===%r===="%(result['weight'] ))
        pickings.number_of_packages = total_package
        return result

    @api.model
    def dhl_get_tracking_link(self,picking):
        return DHLAPI.get_tracking_link(picking.carrier_tracking_ref)
    @api.model
    def dhl_cancel_shipment(self,pickings):
        raise ValidationError('DHL not allow this cancellation of Shipment.')

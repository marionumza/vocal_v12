# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
#################################################################################
import logging
_logger = logging.getLogger(__name__)
from odoo import api, fields, models
from odoo.exceptions import UserError
import requests
try:
    import certifi
except Exception as e:
    _logger.info("< WARNING : No module name certifi>")


from requests.auth import HTTPBasicAuth

ELASTIC_STATUS = False
try:
    from elasticsearch import Elasticsearch
    ELASTIC_STATUS = True
except Exception as e:
    _logger.info("< WARNING : No module name Elasticsearch>")



class ElasticConnection(models.Model):
    _name = 'elastic.connection'

    name = fields.Char(string="Name", required=True)
    host = fields.Char(string="Host ( ip / name)", required=True)
    is_port = fields.Boolean(string="Is Port Available",required=True)
    port = fields.Integer(string="Port")
    url_prefix = fields.Selection(
        [
            ('http', 'Http'),
            ('https', 'Https')
        ], string="Url Prefix", required=True)
    timeout = fields.Integer(string="Timeout", required=True, default=10)
    auth_type = fields.Selection(
        [
            ('http_auth', 'Http Auth'),
            ('other', 'Other')
        ], string="Auth Type")
    user_name = fields.Char(string="User Name")
    user_password = fields.Char(string="Password")
    other_auth_detail = fields.Char(string="Other Auth Detail")

    def _geturl(self):
        return ("%s://%s%s" % (self.url_prefix, self.host,":%s"%self.port if self.is_port else ''))

    @api.multi
    def test_connection(self):
        url = self._geturl()
        _logger.info("< TEST >  URL With %s  , url => %s"%(self.url_prefix,url))
        try:
            if self.url_prefix == 'https' and self.auth_type == 'http_auth':
                res = requests.get(url,auth=HTTPBasicAuth(self.user_name, self.user_password))
            elif  self.url_prefix == 'http':
                res = requests.get(url)
            elif self.url_prefix == 'https' and self.auth_type == 'other':
                raise UserError("For more detail contact to the administrator.")
            else:
                raise UserError("Something went Wrong")
            connectionStatus = self.check_connection(self)
            raise UserError(res.content)
        except Exception as e:
            raise UserError(e)


    def check_connection(self, record):
        result = {'status': False, 'message': ''}
        # url = ("%s://%s:%s" % (record.url_prefix,record.host, record.port))
        url = record._geturl()
        try:

            if self.url_prefix == 'https' and self.auth_type == 'http_auth':
                res = requests.get(url,auth=HTTPBasicAuth(self.user_name, self.user_password))
                result.update({"status": True, "message": "Connection created successfully on ssl","url":url,"reponse":res})
            elif  self.url_prefix == 'http':
                res = requests.get(url)
                result.update({"status": True, "message": "Connection created successfully","url":url,"reponse":res})
            else:
                result.update({"status": False, "message": "Connection not created","url":url})
        except Exception as e:
            result.update({"status": False, "message": "Connection not created","url":url})
        return result


    @api.model
    def _getConfiguration(self):
        result = {'status':False, 'message':''}
        record = self.search([],limit=1)
        if ELASTIC_STATUS:
            if record:
                connectionStatus = record.check_connection(record)
                if connectionStatus['status']:
                    result.update({
                        "url_prefix":record.url_prefix,
                        "host":record.host,
                        'auth_type':record.auth_type,
                        'complete_url':record._geturl(),
                        "http_auth":(record.user_name,record.user_password),
                        "port":record.port,
                        "is_port":record.is_port,
                        "status":True
                        })
                else:
                    result.update(connectionStatus)
            else:
                result.update({"message":"No Configuration Found !!!"})
        else:
            result.update({"message":"No module name Elasticsearch !!!"})
        return result

    @api.model
    def _getConnectionData(self):
        result = self._getConfiguration()
        if result['status']:
            if result['url_prefix'] == 'https' and result['auth_type'] == 'http_auth':
                if result['is_port']:
                    result['elastic_obj'] = Elasticsearch(
                        hosts=[{"host":host,"port":port}],
                        http_auth=result['http_auth'],
                        ca_certs = certifi.where()
                    )
                else:
                    result['elastic_obj'] = Elasticsearch(
                        # ['https://elasticsearch.bitnamiapp.com/elasticsearch'],
                        [result.get("complete_url")],
                        http_auth=result['http_auth'],
                        ca_certs=certifi.where()
                    )
            elif result['url_prefix'] == 'http':
                result['elastic_obj'] = Elasticsearch([{"host":result["host"],"port":result["port"]}])
            else:
                result = {'status': False,"message":"Something wrong in Configuration."}
        return result

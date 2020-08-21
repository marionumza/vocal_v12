
# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
#################################################################################
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError
from odoo import models, fields,api,_
from ast import literal_eval

MODELDOMAIN = [("model","in",("product.template","product.product"))]


class ElasticSearch(models.Model):

    _name = 'elastic.index'

    name = fields.Char(string="Index Name",required=True,help="Name field is the Index Name of elastic search")
    model_id = fields.Many2one('ir.model', string='Model Name',domain= MODELDOMAIN,required=True)
    elastic_fields_mapping_ids = fields.One2many('elastic.field.mapping', 'field_mapping_id', string='Elastic Field Mapping', )
    elastic_domain_fields_ids = fields.One2many('elastic.domain.field', 'domain_field_id', string='Elastic Domain Field ', )
    mapping_count = fields.Integer(string="Mapping Record",compute='_mapping_count')
    doc_type = fields.Char(string="Doc type",required=True)
    description = fields.Text(string="Description")
    domain = fields.Char(string="Domain",compute='_compute_filter',help="Set your domain on Model Name eg.. [('website_published','=',True)]")
    limit =  fields.Integer(string="Limit")
    last_sync_date = fields.Datetime(string='Last Updated', help="Date of last update")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('error', 'Error'),
        ('done', 'Confirm')
    ], 'Status', default='draft', required=True, readonly=True)

    def _compute_filter(self):
        domain = ""
        for obj in self.elastic_domain_fields_ids:
            if obj.field_operator == 'true':
                domain += "('%s','=',True),"%obj.field_name.name
            elif obj.field_operator == 'false':
                domain += "('%s','=',False)," % obj.field_name.name
            else:
                # domain += "('%s','=','%s')," % (obj.field_name.name,obj.field_value)
                pass
        self.domain = "["+domain+"]"


    @api.multi
    def unlink(self):
        mappingObj = self.env["elastic.record.mapping"]
        for rec in self:
            mappingExist = mappingObj.search([("elastic_index_id","=",rec.id)],limit=1)
            if mappingExist.id:
                raise UserError("You can't delete this index.")
            else:
                return super(ElasticSearch, self).unlink()

    @api.one
    def _mapping_count(self):
        count = self.env['elastic.record.mapping'].search_count([('elastic_index_id', '=', self.id)])
        self.mapping_count = count

    @api.onchange('model_id')
    def set_name(self):
        if self.model_id :
            self.name = self.model_id.model.replace(".","-")

    @api.onchange('model_id')
    def set_doc_type(self):
        if self.model_id:
            self.doc_type = self.model_id.model

    @api.multi
    def field_mapping_button(self):
        result = self._create_field_mapping()
        if result.get('status') and result.get('acknowledged'):
            msg = "Index has been created Successfully. Please Create the record from Odoo record to Elastic Search Server by clicking Create/Update Button."
        elif not result.get('status'):
            msg = result['message']
        elif result.get('status') and (not result.get('acknowledged')):
            msg = "You can't create duplicate Index, first reset the index than click on Create Mapping"
        else:
            msg = str(result)
        return self.show_msg_wizard(msg)


    def _create_field_mapping(self,crone=False):
        result = {}
        doc_type = self.doc_type
        connection = self.env['elastic.connection']._getConnectionData()
        fields = self.make_fields()
        if connection.get("status"):
            mapping = {
                "mappings": {
                    doc_type: {
                        "properties": fields
                    }
                }
            }
            esObj = connection['elastic_obj']
            mapResult = esObj.indices.create(index=self.name, ignore=400, body=mapping)
            if mapResult.get("acknowledged"):
                self.state = "done"
            else:
                self.state = "error"
            result.update(mapResult)
        result.update(connection)
        return result


    @api.multi
    def import_data_button(self):
        self.last_sync_date = fields.Datetime.now()
        result = self._allDataImport(crone=False)
        return result

    @api.multi
    def forcely_update_button(self):
        mappingObj = self.env['elastic.record.mapping']
        mapping_ids = mappingObj.search([("elastic_index_id", "=", self.id)])
        for obj in mapping_ids:
            obj.need_sync = True
        connection = self.env['elastic.connection']._getConnectionData()
        fields = self.get_fields()
        update_result = self._update_index(
            fields=fields,
            mappingObj=mappingObj,
            connection=connection
        )
        if update_result.get('status'):
            if  update_result.get('updated_count') > 0:
                msg = "Records updated successfully, total number of updated record(s) %s. " %update_result.get('updated_count')
            else:
                msg =  "No records are affected index is already updated."
        else:
            msg = str(update_result)
        return self.show_msg_wizard(msg)


    def _allDataImport(self,crone):
        result = {"status":False,"message":""}
        mappingObj = self.env['elastic.record.mapping']
        connection = self.env['elastic.connection']._getConnectionData()
        limit = self.limit
        fields = self.get_fields()
        common_domain = []
        if self.domain:
            common_domain += literal_eval(self.domain)
        create_result = self._create_index_record(
            fields = fields,
            common_domain = common_domain,
            mappingObj = mappingObj,
            connection = connection,
            limit = limit
        )
        result.update(create_result)
        update_result = self._update_index(
            fields=fields,
            mappingObj=mappingObj,
            connection=connection
        )
        result.update(update_result)
        if crone:
            return result
        else:
            if result.get('status'):
                if result.get('create_count') > 0 and result.get('updated_count') > 0:
                    msg = "Records synchronize successfully, total number created record(s) %s and total number of updated record(s) %s. "%(result.get('create_count'),result.get('updated_count'))
                elif result.get('create_count') > 0:
                    msg = "Records synchronize successfully, total number created record(s) %s."%result.get('create_count')
                elif result.get('updated_count') > 0:
                    msg = "Records synchronize successfully, total number updated record(s) %s."% result.get('updated_count')
                elif result.get('create_count') == 0 and result.get('updated_count') == 0:
                    msg = "Records synchronize successfully. No records are affected index is already updated."
                else:
                    msg = str(result)
            else:
                msg = str(result)

            return self.show_msg_wizard(msg)



    def _create_index_record(self,fields,limit,common_domain,mappingObj,connection):
        mapRecordIds = mappingObj._get_mapping_ids(
            update=False,
            elastic_index_id=self.id,
            model_id=self.model_id.id,
            index_name=self.name
        )
        record_ids = [i['record_id'] for i in mapRecordIds]
        domain = common_domain + [("id","not in",record_ids)]
        if connection['status']:
            esObj = connection['elastic_obj']
            model_name = self.model_id.model
            index = self.name
            doc_type = self.doc_type
            create_count = 0
            modelObj = self.env[model_name].sudo()
            all_dataObj = modelObj.search_read( domain , fields=fields,limit=limit)
            res = {}
            for obj in all_dataObj:
                vals = {
                    'elastic_index_id': self.id,
                    'model_id': self.model_id.id,
                    'record_id': obj['id'],
                    "description": "",
                    "record_source":'%s,%s' % (self.model_id.model, obj['id'])
                }
                mapId = mappingObj.create(vals)
                try:
                    id = obj.pop('id')
                    res = esObj.index(index=index, doc_type=doc_type, id=id, body=obj)
                except Exception as e:
                    mapId.write({"description":" \n "+ str(e)})
                if res.get("_shards") and  res.get("_shards").get("successful") == 1:
                    create_count += 1
            connection.update({"message": "Record created successfully","create_count":create_count,"status":True})
        return connection




    def _update_index(self,fields,mappingObj,connection):
        mapRecordIds = mappingObj._get_mapping_ids(
            update=True,
            elastic_index_id=self.id,
            model_id=self.model_id.id,
            index_name=self.name
        )
        ids = [i['id'] for i in mapRecordIds]
        domain =[("id","in",ids)]
        mapObjIds = mappingObj.search(domain)
        if connection['status']:
            esObj = connection['elastic_obj']
            model_name = self.model_id.model
            index = self.name
            doc_type = self.doc_type
            modelObj = self.env[model_name].sudo()
            updated_count = 0
            for obj in mapObjIds:
                modelData = modelObj.search_read([("id","=",obj.record_source.id)], fields=fields)
                try:
                    res = esObj.update(index=index, doc_type=doc_type, id=obj.record_source.id, body={"doc":modelData[0]})
                    obj.write({"need_sync": False})
                    if res.get("_id"):
                        updated_count += 1
                except Exception as e:
                    obj.write({"description": " \n " + e})
            connection.update({"message": "Record created/updated successfully","updated_count":updated_count,"status":True})
        return connection




    @api.multi
    def get_data_button(self):
        result = self.env['elastic.connection']._getConnectionData()
        if result['status']:
            esObj = result['elastic_obj']
            try:
                get_data = esObj.search(body={"query": {"match_all": {}}}, index = self.name)
                raise UserError("Data %s" % get_data)
            except Exception as e:
                raise UserError(e)
        else:
            raise UserError("Message %s" % result["message"])



    @api.multi
    def delete_index_button(self):
        result = self.env['elastic.connection']._getConnectionData()
        if result['status']:
            esObj = result['elastic_obj']
            result = esObj.indices.delete(index=self.name, ignore=[400, 404])
            mappingObj = self.env['elastic.record.mapping']
            mapping_ids = mappingObj.search([("elastic_index_id", "=", self.id)])
            for obj in mapping_ids:
                obj.unlink()
            self.state = "draft"
            if result.get('acknowledged'):
                msg = "Index and their mappings are deleted successfully. "
            else:
                self.state = "error"
                msg = "No such index is found in elastic search server."

        else:
            self.state = "error"
            mag = result["message"]
        return self.show_msg_wizard(msg)


    def make_fields(self):
        fields = {}
        for id in self.elastic_fields_mapping_ids:
            fields.update({
                id.name :{ "type": id.field_type  }
            })
        return fields


    def get_fields(self):
        fields = []
        for fld in self.elastic_fields_mapping_ids:
            fields.append(fld.name)
        return fields



    def show_msg_wizard(self,msg):
        partial_id = self.env['wk.wizard.message'].create({'text': msg})
        return {
            'name': "Message",
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'wk.wizard.message',
            'res_id': partial_id.id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
        }

    @api.model
    def process_index_update_scheduler_queue(self):
        mappingObj = self.env['elastic.record.mapping']
        mapping_ids = mappingObj.search([("elastic_index_id", "=", self.id)])
        for obj in mapping_ids:
            obj.need_sync = True
        connection = self.env['elastic.connection']._getConnectionData()
        fields = self.get_fields()
        update_result = self._update_index(
            fields=fields,
            mappingObj=mappingObj,
            connection=connection
        )

    # def _delete_index_record(self,all_ids,mappingObj,connection):
    #     domain = [("elastic_index_id","=",self.id)]
    #     mapIds = mappingObj.search_read(domain,fields=["record_id"])
    #     if connection['status']:
    #         esObj = connection['elastic_obj']
    #         index = self.index
    #         doc_type = self.doc_type
    #         delete_count = 0
    #         for m in mapIds:
    #             if m['record_id'] not in all_ids:
    #                 mapRecord = mappingObj.browse([m['id']])
    #                 try:
    #                     esObj.delete(index=index, doc_type=doc_type, id=m['record_id'])
    #                     delete_count +=1
    #                     mapRecord.unlink()
    #                 except Exception as e:
    #                     mapRecord.write({"description":" \n " +e})
    #         connection.update({"delete_count":delete_count})
    #     return connection



    # def _delete_index(self,mappingObj, connection):
    #     domain = [("record_source","=",False)]
    #     delete_ids = mappingObj.search([])
    #     # _logger.info("---delete_ids--%r-----",delete_ids)
    #     # _logger.info("---delete_ids--%r-----",delete_ids)
    #     _logger.info("---mappingObj--%r-----",mappingObj)
    #
    #     _logger.info("---delete_ids--%r-----",delete_ids)


        # delete_result = self._delete_index(
        #     mappingObj = mappingObj,
        #     connection = connection
        # )



# # @api.onchange('model_id')
    # def _make_field(self):
    #     # model= self.env['ir.model.fields'].search([('model_id','=',self.model_id.id)])
    #     domain = [('model_id','=',self.model_id.id)]
    #     domain +=  FIELDSDOMAIN
    #     return {'domain': {'field_ids': domain }}

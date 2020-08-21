from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = "product.template"

    #
    # @api.multi
    # def write(self,vals):
    #     product_attr = ['description', 'description_sale', 'name','website_published','sale_ok','active']
    #     domain = [("index_name","=","product-template"),("record_id","=",self.id)]
    #     mappingObj = self.env["elastic.record.mapping"].search(domain,limit=1)
    #     result = super(ProductTemplate,self).write(vals)
    #     intersection = list(set(vals.keys()).intersection(product_attr))
    #     if intersection:
    #         mappingObj.write({"need_sync":True})
    #     return result

    # @api.multi
    # def unlink(self):
    #     domain = [("index_name", "=", "product-template"), ("record_id", "=", self.id)]
    #     mappingObj = self.env["elastic.record.mapping"].search(domain,limit=1)
    #     mappingObj.unlink()
    #     return super(ProductTemplate,self).unlink()

    @api.multi
    def write(self,vals):
        result = super(ProductTemplate,self).write(vals)
        product_attr = ['description', 'description_sale', 'name','website_published','sale_ok','active']
        intersection = list(set(vals.keys()).intersection(product_attr))
        if intersection:
            mapObj = self.env["elastic.record.mapping"].sudo()
            for o in self:
                domain = [("index_name","=","product-template"),("record_id","=",o.id)]
                mappingObj = mapObj.search(domain,limit=1)
                mappingObj.write({"need_sync":True})
        return result

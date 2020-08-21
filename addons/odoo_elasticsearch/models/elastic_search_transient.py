from odoo import models,fields,api,_
import logging
_logger = logging.getLogger(__name__)

class ElasticSearchTransient(models.TransientModel):
    _name = 'elastic.search.transient'

    need_sync = fields.Selection(
        [
            ("True","True"),
            ("False","False")],string="Need Sync",required=True)

    @api.multi
    def action_need_sync_apply(self):
        active_ids = self._context.get("active_ids")
        mappingObj = self.env["elastic.record.mapping"].search([("id","in",active_ids)])
        for obj in mappingObj:
            if self.need_sync == "True":
                obj.need_sync = True
            else:
                obj.need_sync = False



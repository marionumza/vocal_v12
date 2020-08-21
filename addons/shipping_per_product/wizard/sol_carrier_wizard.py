# -*- coding: utf-8 -*-
##########################################################################
# 2010-2017 Webkul.
#
# NOTICE OF LICENSE
#
# All right is reserved,
# Please go through this link for complete license : https://store.webkul.com/license.html
#
# DISCLAIMER
#
# Do not edit or add to this file if you wish to upgrade this module to newer
# versions in the future. If you wish to customize this module for your
# needs please refer to https://store.webkul.com/customisation-guidelines/ for more information.
#
# @Author        : Webkul Software Pvt. Ltd. (<support@webkul.com>)
# @Copyright (c) : 2010-2017 Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# @License       : https://store.webkul.com/license.html
#
##########################################################################
from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)

class SolDeliveryCarrier(models.TransientModel):
    _name="sol.delivery.carrier"

    @api.model
    def default_get(self,default_fields):
        res = super(SolDeliveryCarrier,self).default_get(default_fields)
        order_id = self.env['sale.order'].browse(self._context.get('active_id'))
        line_ids = order_id.order_line.filtered(lambda l: l.is_delivery == False)
        res['line_ids'] = line_ids.ids
        return res

    line_ids = fields.Many2many("sale.order.line")
    empty_line = fields.Boolean()

    @api.one
    def set_delivery_line_in_so(self):
        if self.line_ids:
            return self.line_ids[0].order_id.get_delivery_price()
        else:
            pass

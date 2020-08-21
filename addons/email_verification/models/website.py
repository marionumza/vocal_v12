#  -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE URL <https://store.webkul.com/license.html/> for full copyright and licensing details.
#################################################################################
from openerp import api, fields , models
import logging
_logger = logging.getLogger(__name__)

class Website(models.Model):
    _inherit = 'website'
   
    @api.model
    def check_email_is_validated(self):
        current_user = self.env['res.users'].sudo().browse(self._uid)
        status = 'verified'
        restrict_users = self.env['ir.default'].sudo().get('email.verification.config', 'restrict_unverified_users')
        if restrict_users:
            if not current_user.wk_token_verified:
                if not current_user.signup_valid:
                    status = 'expired'
                else:
                    status = 'unverified'
        return status

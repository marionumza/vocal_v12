﻿# © 2017 Nedas Žilinskas <nedas.zilinskas@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResPartnerHCategory(models.Model):

    _inherit = 'res.partner.hcategory'

    forum_ids = fields.Many2many(
        comodel_name='forum.forum',
        string='Allowed Forums',
    )

    inherited_forum_ids = fields.Many2many(
        comodel_name='forum.forum',
        string='Inherited Forums',
        compute='_compute_inherited_forum_ids',
    )

    def _compute_inherited_forum_ids(self):
        for rec in self:
            allowed_forum_ids = []
            hparent_id = rec.parent_id
            while hparent_id:
                allowed_forum_ids += hparent_id.forum_ids.ids
                hparent_id = hparent_id.parent_id
            rec.inherited_forum_ids = [(6, 0, allowed_forum_ids)]

# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning
from odoo.exceptions import UserError, ValidationError
from odoo.addons import decimal_precision as dp
import re
import logging
_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Default methods
    def _get_default_category_id(self):
        if self.marketplace_seller_id:
            mp_categ = self.env['res.config.settings'].sudo().get_values().get('internal_categ')
            if mp_categ:
                return mp_categ.id
        elif self._context.get("pass_default_categ"):
            return False
        return super(ProductTemplate, self)._get_default_category_id()

    # Fields declaration

    categ_id = fields.Many2one(
        'product.category', 'Internal Category',
        change_default=True, default=_get_default_category_id,
        required=True, help="Select category for the current product")
    status = fields.Selection([('draft', 'Draft'), ('pending', 'Pending'), (
        'approved', 'Approved'), ('rejected', 'Rejected')], "Marketplace Status", default=lambda self: "draft" if self.env.user.partner_id and self.env.user.partner_id.seller else False, copy=False, track_visibility='onchange')
    qty = fields.Float(string="Initial Quantity",
                       help="Initial quantity of the product which you want to update in warehouse for inventory purpose.", copy=False)
    template_id = fields.Many2one(
        "product.template", string="Product Template Id", copy=False)
    marketplace_seller_id = fields.Many2one(
        "res.partner", string="Seller", default=lambda self: self.env.user.partner_id.id if self.env.user.partner_id and self.env.user.partner_id.seller else self.env['res.partner'], copy=False, track_visibility='onchange', help="If product has seller then it will consider as marketplace product else it will consider as simple product.")
    color = fields.Integer('Color Index')
    pending_qty_request = fields.Boolean(
        string="Request Pending", compute="_get_pending_qty_request")
    is_initinal_qty_set = fields.Boolean("Initial Qty Set")
    activity_date_deadline = fields.Date(
        'Next Activity Deadline', related='activity_ids.date_deadline',
        readonly=True, store=True,
        groups="base.group_user,odoo_marketplace.marketplace_seller_group")
    description_sale = fields.Text(
        'Sale Description', translate=True, size=500,
        help="A description of the Product that you want to communicate to your customers. "
             "This description will be copied to every Sales Order, Delivery Order and Customer Invoice/Credit Note")
    product_video = fields.Binary('Product Video', attachment=True)
    video_url = fields.Char('Video URL', help='URL of a video for showcasing your product.')
    embed_code = fields.Char(compute="_compute_embed_code")
    # seller_price = fields.Float('Seller Price', digits=dp.get_precision('Product Price'))

    # @api.constrains('description_sale')
    # @api.one
    # def _check_description_sale_len(self):
    #     if self.type == 'product' and self.description_sale and (len(self.description_sale) < 1200 or len(self.description_sale) > 2000):
    #         raise ValidationError('You have typed more/less characters than allowed in Short Product Description (Min: 1200, Max: 2000)')
    #     elif self.type == 'product' and not self.description_sale:
    #         raise ValidationError('Short Product Description Required (Min: 1200, Max: 2000)')

    @api.onchange("standard_price")
    def onchange_seller_price(self):
        self.lst_price = self.standard_price + 50

    @api.depends('video_url')
    def _compute_embed_code(self):
        for product in self:
            product.embed_code = self.get_video_embed_code(product.video_url)

    def get_video_embed_code(self, video_url):
        if not video_url:
            return False

        validURLRegex = r'^(http:\/\/|https:\/\/|\/\/)[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$'

        ytRegex = r'^(?:(?:https?:)?\/\/)?(?:www\.)?(?:youtu\.be\/|youtube(-nocookie)?\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=))((?:\w|-){11})(?:\S+)?$'
        vimeoRegex = r'\/\/(player.)?vimeo.com\/([a-z]*\/)*([0-9]{6,11})[?]?.*'
        dmRegex = r'.+dailymotion.com\/(video|hub|embed)\/([^_]+)[^#]*(#video=([^_&]+))?'
        igRegex = r'(.*)instagram.com\/p\/(.[a-zA-Z0-9]*)'
        ykuRegex = r'(.*).youku\.com\/(v_show\/id_|embed\/)(.+)'

        if not re.search(validURLRegex, video_url):
            return False
        else:
            embedUrl = False
            ytMatch = re.search(ytRegex, video_url)
            vimeoMatch = re.search(vimeoRegex, video_url)
            dmMatch = re.search(dmRegex, video_url)
            igMatch = re.search(igRegex, video_url)
            ykuMatch = re.search(ykuRegex, video_url)

            if ytMatch and len(ytMatch.groups()[1]) == 11:
                embedUrl = '//www.youtube%s.com/embed/%s?rel=0' % (ytMatch.groups()[0] or '', ytMatch.groups()[1])
            elif vimeoMatch:
                embedUrl = '//player.vimeo.com/video/%s' % (vimeoMatch.groups()[2])
            elif dmMatch:
                embedUrl = '//www.dailymotion.com/embed/video/%s' % (dmMatch.groups()[1])
            elif igMatch:
                embedUrl = '//www.instagram.com/p/%s/embed/' % (igMatch.groups()[1])
            elif ykuMatch:
                ykuLink = ykuMatch.groups()[2]
                if '.html?' in ykuLink:
                    ykuLink = ykuLink.split('.html?')[0]
                embedUrl = '//player.youku.com/embed/%s' % (ykuLink)
            else:
                embedUrl = video_url
            return '<iframe class="embed-responsive-item" src="%s" allowFullScreen="true" frameborder="0"></iframe>' % embedUrl

    @api.constrains('video_url')
    def _check_valid_video_url(self):
        for product in self:
            if product.video_url and not product.embed_code:
                raise ValidationError(_("Provided video URL for '%s' is not valid. Please enter a valid video URL.") % product.name)

    def _get_product_video_attachment(self):
        self.ensure_one()
        attachment = self.env['ir.attachment'].sudo().search([('res_model', '=', self._name), ('res_field', '=', 'product_video'), ('res_id', 'in', self.ids)])
        return attachment or False

    @api.model
    def _read_group_fill_results( self, domain, groupby, remaining_groupbys,
        aggregated_fields, count_field,read_group_result, read_group_order=None):

        if groupby == 'status':
            for result in read_group_result:
                state = result['status']
                if state in ['rejected']:
                    result['__fold'] = True
        return super(ProductTemplate, self)._read_group_fill_results(domain, groupby, remaining_groupbys,
            aggregated_fields, count_field, read_group_result, read_group_order)

    # SQL Constraints

    # compute and search field methods, in the same order of fields declaration

    @api.model
    def _get_pending_qty_request(self):
        for obj in self:
            mp_stock_obj = self.env["marketplace.stock"].search(
                [('product_temp_id', '=', obj.id), ('state', '=', 'requested')])
            obj.pending_qty_request = True if mp_stock_obj else False

    # Constraints and onchanges

    @api.onchange("marketplace_seller_id")
    def onchange_seller_id(self):
        self.status = "draft" if self.marketplace_seller_id and not self.status else False
        self.categ_id = self.env['res.config.settings'].sudo().get_values().get('internal_categ')

    # CRUD methods (and name_get, name_search, ...) overrides

    @api.model
    def create(self, vals):
        ''' Set default false to sale_ok and purchase_ok for seller product'''
        partner = self.env["res.partner"].sudo().browse(vals.get("marketplace_seller_id", False)) or self.env.user.partner_id
        if partner and partner.sudo().seller:
            if not vals.get("sale_ok", False):
                vals["sale_ok"] = False
            if not vals.get("purchase_ok", False):
                vals["purchase_ok"] = False
            vals["type"] = "product"
            if not vals.get("status", False):
                vals["status"] = "draft"
            if not vals.get("invoice_policy", False):
                vals["invoice_policy"] = "delivery"
            config_setting_obj = self.env[
                'res.config.settings'].sudo().get_values()
            if config_setting_obj.get('internal_categ'):
                vals["categ_id"] = config_setting_obj['internal_categ']
        if vals.get('standard_price'):
            vals.update({'lst_price': vals.get('standard_price') + 50})
        product_template = super(ProductTemplate, self).create(vals)
        return product_template

    # Action methods

    @api.multi
    def toggle_website_published(self):
        """ Inverse the value of the field ``website_published`` on the records in ``self``. """
        for record in self:
            record.website_published = not record.website_published

    @api.multi
    def mp_action_view_sales(self):
        self.ensure_one()
        action = self.env.ref('odoo_marketplace.wk_seller_slae_order_line_action')
        product_ids = self.product_variant_ids.ids
        tree_view_id = self.env.ref('odoo_marketplace.wk_seller_product_order_line_tree_view')
        form_view_id = self.env.ref('odoo_marketplace.wk_seller_product_order_line_form_view')
        return {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'views': [(tree_view_id.id, 'tree'), (form_view_id.id, 'form')],
            'target': action.target,
            'context': "{'default_product_id': " + str(product_ids[0]) + "}",
            'res_model': action.res_model,
            'domain': [('state', 'in', ['sale', 'done']), ('product_id.product_tmpl_id', '=', self.id)],
        }

    @api.multi
    def pending_qty_stock_request(self):
        for rec in self:
            pending_stock = self.env["marketplace.stock"].search([('product_temp_id','=',rec.id),('state','=','requested')])
            return {
                'name':'Update Marketplace Product Quantity',
                'type':'ir.actions.act_window',
                'res_model':'marketplace.stock',
                'view_mode':'form',
                'view_type':'form',
                'res_id' : pending_stock[0].id,
                'target':'current',
            }

    # Business methods

    @api.one
    def send_mail_to_seller(self, mail_templ_id):
        """ """
        if not mail_templ_id:
            return False
        template_obj = self.env['mail.template'].browse(mail_templ_id)
        template_obj.send_mail(self.id, True)

    @api.multi
    def auto_approve(self):
        for obj in self:
            if obj.marketplace_seller_id.auto_product_approve:
                obj.write({"status": "pending"})
                obj.sudo().approved()
            else:
                obj.write({"status": "pending"})
        return True

    @api.one
    def check_state_send_mail(self):
        config_setting_obj = self.env['res.config.settings'].sudo().get_values()
        for obj in self.filtered(lambda o: o.status in ["approved", "rejected"]):
            temp_id = temp_id2 = False
            if obj.status == "approved":
                temp_id = config_setting_obj["notify_admin_on_product_approve_reject_m_tmpl_id"]
                temp_id2 = config_setting_obj["notify_seller_on_product_approve_reject_m_tmpl_id"]
            elif obj.status == "rejected":
                temp_id = config_setting_obj["notify_admin_on_product_approve_reject_m_tmpl_id"]
                temp_id2 = config_setting_obj["notify_seller_on_product_approve_reject_m_tmpl_id"]
            # Notify to admin by admin when product approved/rejct
            if config_setting_obj["enable_notify_admin_on_product_approve_reject"] and config_setting_obj.get("notify_admin_on_product_approve_reject_m_tmpl_id", False):
                if temp_id:
                    self.send_mail_to_seller(temp_id)
            # Notify to Seller by admin  when product approved/rejct
            if config_setting_obj["enable_notify_seller_on_product_approve_reject"] and config_setting_obj.get("notify_seller_on_product_approve_reject_m_tmpl_id", False):
                if temp_id2:
                    self.send_mail_to_seller(temp_id2)


    @api.multi
    def approved(self):
        for obj in self:
            if not obj.marketplace_seller_id:
                raise Warning(_("Marketplace seller id is not assign to this product."))
            if obj.marketplace_seller_id.state == "approved":
                obj.sudo().write({"status": "approved", "sale_ok": True})
                obj.check_state_send_mail()
                if not obj.is_initinal_qty_set:
                    obj.set_initial_qty()
            else:
                raise Warning(
                    _("Marketplace seller of this product is not approved."))
        return True

    @api.multi
    def reject(self):
        for product_obj in self:
            if product_obj.status in ("draft", "pending", "approved") and product_obj.marketplace_seller_id:
                product_obj.write({
                    "sale_ok": False,
                    "website_published": False,
                    "status": "rejected"
                })
                product_obj.check_state_send_mail()

    # Called in server action
    @api.multi
    def approve_product(self):
        self.filtered(lambda o: o.status == "pending" and o.marketplace_seller_id).approved()

    # Called in server action
    @api.multi
    def reject_product(self):
        self.filtered(lambda o: o.status in ("draft", "pending", "approved") and o.marketplace_seller_id).reject()

    @api.multi
    def set_initial_qty(self):
        for template_obj in self:
            if len(self) == 1:
                if template_obj.qty < 0:
                    raise Warning(_('Initial Quantity can not be negative'))
            if not template_obj.marketplace_seller_id.location_id:
                raise Warning(_("Product seller has no location/warehouse."))
            if template_obj.qty > 0:
                vals = {
                    'product_id': template_obj.product_variant_ids[0].id,
                    'product_temp_id': template_obj.id,
                    'new_quantity': template_obj.qty,
                    'location_id': template_obj.marketplace_seller_id.location_id.id or False,  # Phase 2
                    'note': _("Initial Quantity."),
                    'state': "requested",
                }
                mp_product_stock = self.env['marketplace.stock'].create(vals)
                template_obj.is_initinal_qty_set = True
                mp_product_stock.auto_approve()

    def disable_seller_all_products(self, seller_id):
        if seller_id:
            product_objs = self.search(
                [("marketplace_seller_id", "=", seller_id), ("status", "not in", ["draft", "rejected"])])
            product_objs.reject()

    @api.multi
    def set_pending(self):
        for rec in self:
            rec.auto_approve()

    @api.multi
    def send_to_draft(self):
        for rec in self:
            rec.write({"status": "draft"})

    @api.multi
    def write(self, vals):
        if vals.get("marketplace_seller_id", False):
            for rec in self:
                if rec.marketplace_seller_id and rec.status not in ["draft", "pending"]:
                    raise UserError(_('You cannot change the seller of the product that already contains seller.'))
        if vals.get('standard_price'):
            vals.update({'lst_price': vals.get('standard_price') + 50})
        return super(ProductTemplate, self).write(vals)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    activity_date_deadline = fields.Date(
        'Next Activity Deadline', related='activity_ids.date_deadline',
        readonly=True, store=True,
        groups="base.group_user,odoo_marketplace.marketplace_seller_group")

    # Action methods

    @api.multi
    def toggle_website_published(self):
        """ Inverse the value of the field ``website_published`` on the records in ``self``. """
        for record in self:
            record.product_tmpl_id.toggle_website_published()

    @api.multi
    def mp_action_view_sales(self):
        self.ensure_one()
        action = self.env.ref('odoo_marketplace.wk_seller_slae_order_line_action')
        tree_view_id = self.env.ref('odoo_marketplace.wk_seller_product_order_line_tree_view')
        form_view_id = self.env.ref('odoo_marketplace.wk_seller_product_order_line_form_view')
        return {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'views': [(tree_view_id.id, 'tree'), (form_view_id.id, 'form')],
            'target': action.target,
            'context': "{'default_product_id': " + str(self.id) + "}",
            'res_model': action.res_model,
            'domain': [('state', 'in', ['sale', 'done']), ('product_id', '=', self.id)],
        }

    @api.multi
    def pending_qty_stock_request(self):
        for rec in self:
            pending_stock = self.env["marketplace.stock"].search([('product_id','=',rec.id),('state','=','requested')])
            return {
                'name':'Update Marketplace Product Quantity',
                'type':'ir.actions.act_window',
                'res_model':'marketplace.stock',
                'view_mode':'form',
                'view_type':'form',
                'res_id' : pending_stock[0].id,
                'target':'current',
            }

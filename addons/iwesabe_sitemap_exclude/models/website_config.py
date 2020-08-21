import datetime
from odoo import models, fields, api
SITEMAP_CACHE_TIME = datetime.timedelta(hours=12)
LOC_PER_SITEMAP = 45000


class WebsiteModel(models.Model):
    _inherit = 'website'

    sitemap_exclude_urls = fields.Text()


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sitemap_exclude_urls = fields.Text(related='website_id.sitemap_exclude_urls', readonly=False)

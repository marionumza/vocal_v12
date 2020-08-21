import datetime
from odoo import models, fields, http, api
from odoo.http import request
from odoo.addons.website.models.ir_http import sitemap_qs2dom
from odoo.osv.expression import FALSE_DOMAIN
SITEMAP_CACHE_TIME = datetime.timedelta(hours=12)
LOC_PER_SITEMAP = 45000


class Website(models.Model):
    _inherit = "website"

    @api.multi
    def enumerate_pages_2(self, query_string=None, force=False):
        """ Available pages in the website/CMS. This is mostly used for links
            generation and can be overridden by modules setting up new HTML
            controllers for dynamic pages (e.g. blog).
            By default, returns template views marked as pages.
            :param str query_string: a (user-provided) string, fetches pages
                                     matching the string
            :returns: a list of mappings with two keys: ``name`` is the displayable
                      name of the resource (page), ``url`` is the absolute URL
                      of the same.
            :rtype: list({name: str, url: str})
        """

        router = request.httprequest.app.get_db_router(request.db)
        # Force enumeration to be performed as public user
        url_set = set()

        sitemap_endpoint_done = set()

        for rule in router.iter_rules():
            if 'sitemap' in rule.endpoint.routing:
                if rule.endpoint in sitemap_endpoint_done:
                    continue
                sitemap_endpoint_done.add(rule.endpoint)

                func = rule.endpoint.routing['sitemap']
                if func is False:
                    continue
                for loc in func(self.env, rule, query_string):
                    new_loc = self.check_loc(loc)
                    if new_loc:
                        yield new_loc
                continue

            if not self.rule_is_enumerable(rule):
                continue

            converters = rule._converters or {}
            if query_string and not converters and (query_string not in rule.build([{}], append_unknown=False)[1]):
                continue
            values = [{}]
            # converters with a domain are processed after the other ones
            convitems = sorted(
                converters.items(),
                key=lambda x: (hasattr(x[1], 'domain') and (x[1].domain != '[]'), rule._trace.index((True, x[0]))))

            for (i, (name, converter)) in enumerate(convitems):
                newval = []
                for val in values:
                    query = i == len(convitems) - 1 and query_string
                    if query:
                        r = "".join([x[1] for x in rule._trace[1:] if not x[0]])  # remove model converter from route
                        query = sitemap_qs2dom(query, r, self.env[converter.model]._rec_name)
                        if query == FALSE_DOMAIN:
                            continue
                    for value_dict in converter.generate(uid=self.env.uid, dom=query, args=val):
                        newval.append(val.copy())
                        value_dict[name] = value_dict['loc']
                        del value_dict['loc']
                        newval[-1].update(value_dict)
                values = newval

            for value in values:
                domain_part, url = rule.build(value, append_unknown=False)
                if not query_string or query_string.lower() in url.lower():
                    page = {'loc': url}
                    for key, val in value.items():
                        if key.startswith('__'):
                            page[key[2:]] = val
                    if url in ('/sitemap.xml',):
                        continue
                    if url in url_set:
                        continue
                    url_set.add(url)
                    new_loc = self.check_loc(page)
                    if new_loc:
                        yield new_loc

        # '/' already has a http.route & is in the routing_map so it will already have an entry in the xml
        domain = [('url', '!=', '/')]
        if not force:
            domain += [('website_indexed', '=', True)]
            # is_visible
            domain += [('website_published', '=', True), '|', ('date_publish', '=', False),
                       ('date_publish', '<=', fields.Datetime.now())]

        if query_string:
            domain += [('url', 'like', query_string)]

        pages = self.get_website_pages(domain)

        for page in pages:

            record = {'loc': page['url'], 'id': page['id'], 'name': page['name']}
            if page.view_id and page.view_id.priority != 16:
                record['__priority'] = min(round(page.view_id.priority / 32.0, 1), 1)
            if page['write_date']:
                record['__lastmod'] = page['write_date'].date()

            new_loc = self.check_loc(record)
            if new_loc:
                yield new_loc

    def check_loc(self, data):
        # Exclude
        if self and self.sitemap_exclude_urls:
            urls = self.sitemap_exclude_urls.split('\n')
            urls = [x.strip() for x in urls if x.strip()]
            if data['loc'] in urls:
                return False
        return data

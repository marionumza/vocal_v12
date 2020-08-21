from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def set_sol_delivery_charge(self, sol):
        return super(SaleOrder, self.with_context(sale_order_line=sol)).set_sol_delivery_charge(sol)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    es_service_id = fields.Many2one("es.service.charge", string="EasyShip Service", ondelete="restrict", copy=False)

    def set_sol_delivery_charge(self, sol):
        order_line_id = self.env["sale.order.line"].browse(int(sol))
        inactive_sol = self.order_line.filtered(lambda l: l.id != order_line_id.id)
        inactive_sol.write({'active': False})

        order = self.browse(self.id)
        order.delivery_rating_success = False
        order_line_id.write({
            'is_delivered': True
        })
        res = order.carrier_id.rate_shipment(order)

        order_line_id.write({
            'delivery_carrier_id': order.carrier_id.id,
            'delivery_charge': res["price"],
            'is_delivered': True
        })

        inactive_sol.write({'active': True})
        return res

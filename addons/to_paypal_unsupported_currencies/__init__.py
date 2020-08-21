from . import models
from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    PaymentAcquirer = env['payment.acquirer']
    default_paypal_currency = PaymentAcquirer._default_paypal_currency()
    PaymentAcquirer.search([('provider', '=', 'paypal')]).write({'paypal_default_currency_id': default_paypal_currency.id})

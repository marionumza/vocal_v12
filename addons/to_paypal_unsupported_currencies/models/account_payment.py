from odoo import models, fields


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    paypal_original_unsupported_currency_id = fields.Many2one('res.currency', string='Paypal Original Unsupported Currency',
                                                              help="A technical field to store the original Paypal unsupported currency"
                                                              " in case of payment with Paypal using a currency that is not supported by Paypal.")
    paypal_original_unsupported_currency_amount = fields.Monetary(string='Paypal Original Unsupported Currency Amount',
                                                                  currency_field='paypal_original_unsupported_currency_id',
                                                                  help="A technical field to store the original Paypal unsupported currency amount"
                                                                  " in case of payment with Paypal using a currency that is not supported by Paypal.")


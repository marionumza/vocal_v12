import json

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

PAYPAL_SUPPORTED_CURRENCIES = [
    'AUD',  # Australian dollar
    'BRL',  # Brazilian real, [2]
    'CAD',  # Canadian dollar
    'CZK',  # Czech koruna
    'DKK',  # Danish krone
    'EUR',  # Euro
    'HKD',  # Hong Kong dollar
    'HUF',  # Hungarian forint [1]
    'INR',  # Indian rupee [3]
    'ILS',  # Israeli new shekel
    'JPY',  # Japanese yen [1]
    'MYR',  # Malaysian ringgit [2]
    'MXN',  # Mexican peso
    'TWD',  # New Taiwan dollar [1]
    'NZD',  # New Zealand dollar
    'NOK',  # Norwegian krone
    'PHP',  # Philippine peso
    'PLN',  # Polish złoty
    'GBP',  # Pound sterling
    'RUB',  # Russian ruble
    'SGD',  # Singapore dollar
    'SEK',  # Swedish krona
    'CHF',  # Swiss franc
    'THB',  # Thai baht
    'USD',  # United States dollar
    # [1] This currency does not support decimals. If you pass a decimal amount, an error occurs.
    # [2] This currency is supported as a payment currency and a currency balance for in-country PayPal accounts only.
    # [3] This currency is supported as a payment currency and a currency balance for in-country PayPal India accounts only.
    ]


class AcquirerPaypal(models.Model):
    _inherit = 'payment.acquirer'

    paypal_default_currency_id = fields.Many2one('res.currency', string='Default Paypal Currency',
                                                 help="The currency supported by Paypal that will be used for payment conversion"
                                                 " for currencies that are not supported by Paypal.\n"
                                                 "For example, your invoice is in VND (Vietnam Dong) which is not supported by Paypal."
                                                 " During online payment, Odoo will convert the amount in VND to the amount in the"
                                                 " currency specified here before processing payment.")

    @api.model
    def _default_paypal_currency(self):
        return self.env.ref('base.USD', raise_if_not_found=False) or self.env['res.currency'].with_context(active_test=False).search([('name', '=', 'USD')], limit=1)

    @api.constrains('paypal_default_currency_id')
    def _check_paypal_default_currency(self):
        for r in self:
            if r.paypal_default_currency_id and r.paypal_default_currency_id.name not in PAYPAL_SUPPORTED_CURRENCIES:
                raise ValidationError(_("The currency %s that you have selected is not supported by Paypal.")
                                      % (r.paypal_default_currency_id.name,))

    @api.multi
    def paypal_form_generate_values(self, values):
        """
        This override is to customize transaction values send to Paypal
        """
        paypal_tx_values = super(AcquirerPaypal, self).paypal_form_generate_values(values)

        # if the currency is not accepted by Paypal and there is an accepted currency defined for the paypal acquirer
        if paypal_tx_values['currency_code'] not in PAYPAL_SUPPORTED_CURRENCIES and self.paypal_default_currency_id:
            unsupported_currency_id = self.env['res.currency'].search([('name', '=', paypal_tx_values['currency_code'])], limit=1)
            amount = unsupported_currency_id._convert(paypal_tx_values['amount'], self.paypal_default_currency_id, self.company_id, fields.Date.today())

            # modify the value of the custom key of the paypal_tx_values
            custom = paypal_tx_values.get('custom', '{}')
            custom = json.loads(custom)
            custom.update({
                'unsupported_currency_amount': paypal_tx_values['amount'],
                'unsupported_currency_code': paypal_tx_values['currency_code'],
                })

            # modify the paypal_tx_values with new amount and currency that are accepted by Paypal,
            # plus custom data that include the original unsuppoted currency and amount in that currency
            paypal_tx_values.update({
                'amount':amount,
                'currency_code': self.paypal_default_currency_id.name,
                'custom': json.dumps(custom),
                })
        return paypal_tx_values


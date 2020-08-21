import json

from odoo import models, fields, api

from .payment_acquirer import PAYPAL_SUPPORTED_CURRENCIES


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    @api.multi
    def _prepare_account_payment_vals(self):
        """
        This override is to ensure the account.payment record generated in Odoo is in the currency that is recorded in Paypal

        Explaination: when request payment in a currency that is not accepted by Paypal, we convert the amount to an accepted currency
            Without this override, the account.payment record will be encoded in the original currency while the corresponding in Paypal is in another one
        """
        self.ensure_one()
        data = super(PaymentTransaction, self)._prepare_account_payment_vals()
        if self.provider == 'paypal':

            # we record payment in the currency processed by paypal
            # for example, invoice is in VND, but paypal use USD. So, the payment record in Odoo should be USD
            if self.currency_id.name not in PAYPAL_SUPPORTED_CURRENCIES and self.acquirer_id.paypal_default_currency_id:
                amount = self.currency_id._convert(
                    self.amount,
                    self.acquirer_id.paypal_default_currency_id,
                    self.acquirer_id.company_id,
                    self.date and self.date.date() or fields.Date.today()
                    )
                injected_data = {
                    'paypal_original_unsupported_currency_id': data['currency_id'],
                    'paypal_original_unsupported_currency_amount': data['amount'],
                    'amount': amount,
                    'currency_id': self.acquirer_id.paypal_default_currency_id.id
                    }
                data.update(injected_data)
        return data

    @api.multi
    def _paypal_form_get_invalid_parameters(self, data):
        """
        This method modifies the mc_gross and mc_currency to its original values they were before being converted to a Paypal accepted currency
        Without this, mc_gross and mc_currency will be considered as invalid. For example,
        
        Invoice is 23000 VND and this amount was converted to US$100 for Paypal payment processing.
        When Paypal notifies Odoo, it return $100 and USD then Odoo would compare it with 23000 and VND, then simply failed.
        """
        custom = data['custom']
        if 'unsupported_currency_code' in custom and 'unsupported_currency_amount' in custom:
            # convert custom from json string to dict
            custom = json.loads(custom)

            # then modify the mc_gross and mc_currency to the values they were before conversion for Paypal
            data.update({
                'mc_gross': custom['unsupported_currency_amount'],
                'mc_currency': custom['unsupported_currency_code']
                })
        return super(PaymentTransaction, self)._paypal_form_get_invalid_parameters(data)

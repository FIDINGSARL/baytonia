from odoo import models, fields


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    eg_magento_payment_method_id = fields.Many2one("magento.payment.method", "M Payment Method")

from odoo import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    # payment_gateway_id = fields.Many2one("woo.payment.gateway", "Payment Gateway")

    @api.onchange('purchase_id')
    def purchase_order_change(self):
        if not self.purchase_id:
            return {}
        self.date_invoice = self.purchase_id.date_order
        return super(AccountInvoice, self).purchase_order_change()

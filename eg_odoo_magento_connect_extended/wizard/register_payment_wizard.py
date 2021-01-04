from odoo import models, fields, api


class RegisterPaymentWizard(models.TransientModel):
    _name = "register.payment.wizard"

    journal_id = fields.Many2one('account.journal', 'Journal', required=True,
                                 help="Payment will be registered with this Journal")
    sale_order_id = fields.Many2one("sale.order", "Sale Order", readonly=True)

    @api.model
    def default_get(self, fields_list):
        res = super(RegisterPaymentWizard, self).default_get(fields_list)
        order_id = self._context.get('active_id')
        if 'sale_order_id' in fields_list:
            res.update({'sale_order_id': order_id})
        return res

    @api.multi
    def register_payment(self):
        for inv in self.sale_order_id.invoice_ids:
            if inv.state == 'open':
                inv.pay_and_reconcile(self.journal_id.id, pay_amount=inv.residual, date=self.sale_order_id.date_order,
                                      writeoff_acc=None)
                break

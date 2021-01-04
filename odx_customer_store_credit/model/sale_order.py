from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    store_credit = fields.Float("Store Credit")
    store_credit_balance = fields.Float("Store Credit Balance")

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.store_credit = self.partner_id.store_credit

    @api.depends('order_line.price_total','store_credit')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            if order.ecommerce_channel == 'magento':
                store_credit = order.store_credit
            else:
                if amount_untaxed + amount_tax >= order.store_credit:
                    store_credit = order.store_credit
                else:
                    store_credit = amount_untaxed + amount_tax
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax - store_credit
            })

    @api.multi
    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        amount_backorder = qt_to_invoice = product_uom_qty = 0.0
        for line in self.order_line:
            qt_to_invoice += line.qty_to_invoice
            amount_backorder += line.price_unit * line.qty_to_invoice
            product_uom_qty += line.product_uom_qty

        store_credit_total = self.store_credit_balance
        if store_credit_total <= amount_backorder:
            store_credit_to_invoice = store_credit_total
        else:
            store_credit_to_invoice = amount_backorder

        self.store_credit_balance = self.store_credit_balance - store_credit_to_invoice
        invoice_vals['store_credit'] = store_credit_to_invoice

        return invoice_vals

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for line in self.order_line:
            amount_untaxed = amount_tax= 0.0
            for line in self.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            store_credit_total = amount_untaxed + amount_tax - self.amount_total
            self.store_credit = store_credit_total
            self.store_credit_balance = store_credit_total
        return res



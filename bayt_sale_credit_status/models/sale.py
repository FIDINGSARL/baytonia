from odoo import models,api,fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.depends('state', 'order_line.invoice_status')
    def _compute_status(self):
        for order in self:
            total = 0
            invoice_ids = order.order_line.mapped('invoice_lines').mapped('invoice_id').filtered(
                lambda r: r.type in ['out_refund'])
            refunds = invoice_ids.search(
                [('origin', 'like', order.name), ('company_id', '=', order.company_id.id)]).filtered(
                lambda r: r.type in ['out_invoice', 'out_refund'])
            invoice_ids |= refunds.filtered(lambda r: order.name in [origin.strip() for origin in r.origin.split(',')])
            # Search for refunds as well
            refund_ids = self.env['account.invoice'].browse()
            if invoice_ids:
                for inv in invoice_ids:
                    refund_ids += refund_ids.search(
                        [('type', '=', 'out_refund'), ('origin', '=', inv.number), ('origin', '!=', False),
                         ('journal_id', '=', inv.journal_id.id)])

            if refund_ids:
                order.credit_status = True
                for invoice in refund_ids:
                    total += invoice.amount_total
                order.credit_amount = total

    credit_status = fields.Boolean('Credit Status', compute='_compute_status')
    credit_amount = fields.Monetary('Credit_amount', compute='_compute_status', store=True)
from odoo import models, fields, api
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    is_return_do = fields.Boolean("Return Do")

    @api.multi
    def return_delivery(self):
        self.ensure_one()
        if self.state == 'done':
            if self.sale_id:
                if self.sale_id.invoice_ids:
                    self.is_return_do = True
                    invoices = self.invoice_id

                    # create creditenotes

                    created_inv = []
                    date = False
                    description = 'refund'
                    if invoices:
                        for inv in invoices:
                            if inv.state == 'paid':
                                raise UserError(('Cannot create credit note for the paid invoice.'))
                            if inv.reconciled:
                                continue
                            date = fields.Date.today() or False
                            description = description or inv.name
                            refund = inv.refund(date, date, description, inv.journal_id.id)
                            created_inv.append(refund.id)
                            movelines = inv.move_id.line_ids
                            to_reconcile_ids = {}
                            to_reconcile_lines = self.env['account.move.line']
                            for line in movelines:
                                if line.account_id.id == inv.account_id.id:
                                    to_reconcile_lines += line
                                    to_reconcile_ids.setdefault(line.account_id.id, []).append(line.id)
                                if line.reconciled:
                                    line.remove_move_reconcile()
                            refund.action_invoice_open()
                            for tmpline in refund.move_id.line_ids:
                                if tmpline.account_id.id == inv.account_id.id:
                                    to_reconcile_lines += tmpline
                            to_reconcile_lines.filtered(lambda l: l.reconciled == False).reconcile()
                        self.sale_id.payment_status = 'failed'

                # create returns

                wizard = self.env['stock.return.picking'].with_context({
                    'active_id': self.id
                }).create({'picking_id': self.id})
                return_picking = wizard.create_returns()
                return_picking_id = self.search([('id', '=', return_picking['res_id'])])
                m_payment_method = self.env['magento.payment.method'].search(
                    [('code', 'like', 'FAILED')], limit=1)
                if m_payment_method:
                    return_picking_id.eg_magento_payment_method_id = m_payment_method.id
                return_picking_id.button_validate()
                for move in return_picking_id.move_lines.filtered(lambda m: m.state not in ['done', 'cancel']):
                    for move_line in move.move_line_ids:
                        move_line.qty_done = move_line.product_uom_qty
                if return_picking_id:
                    return_picking_id.action_done()

        else:
            raise UserError(('There is no invoice.'))
            # self.do_unreserve()
            # self.action_cancel()

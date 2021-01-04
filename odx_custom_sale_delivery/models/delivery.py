from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    order_dispatching = fields.Float('Order Dispatching',compute='_compute_order_dispatching')

    # @api.constrains('date_done', 'create_date')
    # def _compute_order_dispatching(self):
    #     for picking in self:
    #         if picking.date_done and picking.create_date:
    #             time_diff = fields.Datetime.from_string(picking.date_done) - fields.Datetime.from_string(
    #                 picking.create_date)
    #             picking.order_dispatching = time_diff.days

    @api.depends('date_done', 'create_date')
    def _compute_order_dispatching(self):
        for picking in self:
            if picking.date_done and picking.create_date:
                time_diff = fields.Datetime.from_string(picking.date_done) - fields.Datetime.from_string(
                    picking.create_date)
                picking.order_dispatching = time_diff.days


    @api.multi
    def action_done(self):
        result = super(StockPicking, self).action_done()
        description = 'refund'
        move_lines = []
        is_return = False
        is_reconciled = False
        for picking in self:
            auto_payment = False
            if picking.sale_id:
                if picking.invoice_id:
                    invoices_new = self.env['account.invoice'].search([('id', '=', picking.invoice_id.id)])
                else:
                    try:
                        invoivelist = picking.sale_id.action_invoice_create(grouped=False, final=True)
                        invoices_new = self.env['account.invoice'].search([('id', 'in', invoivelist)])
                        for inv in invoices_new:
                            picking.invoice_id = inv.id
                            if inv.amount_total > 0:
                                inv.action_invoice_open()

                    except:
                        pass
                for moves in picking.move_lines:
                    if moves.origin_returned_move_id:
                        is_return = True
                if picking.sale_id.eg_magento_payment_method_id:
                    if picking.sale_id.eg_magento_payment_method_id.is_auto_payment:
                        auto_payment = True
                if picking.sale_id.is_auto_payment or auto_payment:
                    if is_return:
                        try:
                            date = fields.Date.today() or False
                            description = description or inv.name
                            for inv in picking.invoice_id:
                                refund = inv.refund(inv.date_invoice, date, description, inv.journal_id.id)
                        except:
                            pass
                    else:
                        # invoivelist = picking.sale_id.action_invoice_create(grouped=False, final=True)
                        invoices = self.sale_id.invoice_ids
                        # invoices_new = self.env['account.invoice'].search([('id', 'in', invoivelist)])
                        for inv in invoices_new:
                            # picking.invoice_id = inv.id
                            # inv.action_invoice_open()
                            if picking.sale_id.account_payment_id:
                                picking.sale_id.account_payment_id.update({
                                    'invoice_ids': [(6, 0, invoices.ids)]
                                })
                            for lines in inv.move_id.line_ids:
                                move_lines.append(lines)
                        for move_llines in picking.sale_id.account_payment_id.move_line_ids:
                            move_lines.append(move_llines)
                            if move_llines.reconciled:
                                is_reconciled = True
                        account_move_lines_to_reconcile = self.env['account.move.line']
                        if not is_reconciled:
                            for line in move_lines:
                                if line.account_id.internal_type == 'receivable':
                                    account_move_lines_to_reconcile |= line
                            account_move_lines_to_reconcile.filtered(
                                lambda l: l.reconciled == False).reconcile()
        return result

    @api.multi
    def action_create_invoice(self):
        for picking in self:
            if picking.sale_id:
                try:
                    invoivelist = picking.sale_id.action_invoice_create(grouped=False, final=True)
                    invoices_new = self.env['account.invoice'].search([('id', 'in', invoivelist)])
                    for inv in invoices_new:
                        picking.invoice_id = inv.id
                except:
                    pass

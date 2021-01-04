from odoo import models, api, fields
from odoo.http import request
from odoo.tools import float_is_zero, float_compare


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    store_credit = fields.Float("Store Credit")

    def action_invoice_open(self):
        res = super(AccountInvoice, self).action_invoice_open()
        for record in self:
            if record.type == 'out_invoice':
                if record.partner_id:
                    if record.store_credit > 0:
                        move_lines = []
                        amount = record.store_credit
                        account_move_lines_to_reconcile_invoice = self.env['account.move.line']
                        account_move_lines_to_reconcile_refund = self.env['account.move.line']
                        journal_id = self.env['account.journal'].search([], limit=1)
                        receivalbe = self.env['account.account'].search(
                            [('user_type_id.name', 'like', 'Receivable')], limit=1)

                        journal_items = []
                        journal_entry_obj = self.env['account.move']
                        move_lines_refund = []
                        journal_entry_line_obj = self.env['account.move.line']
                        if record.partner_id.parent_id:
                            if record.partner_id.parent_id.store_credit > 0:
                                journal_items.append((0, 0, {'account_id': receivalbe.id,
                                                             'debit': amount,
                                                             'partner_id': record.partner_id.parent_id.id
                                                             }))
                                journal_items.append((0, 0, {'account_id': receivalbe.id,
                                                             'credit': amount,
                                                             'partner_id': record.partner_id.parent_id.id
                                                             }))

                                vals = {
                                    'journal_id': journal_id.id,
                                    "ref": 'Store credit',
                                    "line_ids": journal_items,

                                }
                                journal_entry = journal_entry_obj.create(vals)
                                for items in journal_entry.line_ids:
                                    if items.debit == amount:
                                        move_lines_refund.append(items)
                                    if items.credit == amount:
                                        move_lines.append(items)

                                journal_entry.post()

                                for lines in record.move_id.line_ids:
                                    move_lines.append(lines)


                                for line in move_lines:
                                    if line.account_id.internal_type == 'receivable':
                                        account_move_lines_to_reconcile_invoice |= line

                                account_move_lines_to_reconcile_invoice.filtered(
                                    lambda l: l.reconciled == False).reconcile()

                                refunded_lines = self.env['account.move.line'].search(
                                    [('partner_id', '=', record.partner_id.parent_id.id),
                                     ('account_id.internal_type', '=', 'receivable')])

                                for lines_refund in refunded_lines:
                                    if lines_refund not in move_lines:
                                        move_lines_refund.append(lines_refund)

                                for line in move_lines_refund:
                                    if line.account_id.internal_type == 'receivable':
                                        account_move_lines_to_reconcile_refund |= line
                                account_move_lines_to_reconcile_refund.filtered(
                                    lambda l: l.reconciled == False).reconcile()

                                balance_change = 0
                                if record.partner_id.parent_id.store_credit > amount:
                                    balance_change = -amount
                                    record.partner_id.parent_id.store_credit = record.partner_id.parent_id.store_credit - amount
                                else:
                                    balance_change = -record.partner_id.parent_id.store_credit
                                    record.partner_id.parent_id.store_credit = 0
                                ticket_user_line_obj = self.env['store.credit.history']
                                ticket_user_line_obj.create({
                                    'balance_change': balance_change,
                                    'new_balance': record.partner_id.parent_id.store_credit,
                                    'partner_id': record.partner_id.parent_id.id,
                                    'user_id': self.env.user.id,
                                })
                        else:
                            if record.partner_id.store_credit > 0:

                                journal_items.append((0, 0, {'account_id': receivalbe.id,
                                                             'debit': amount,
                                                             'partner_id': record.partner_id.id
                                                             }))
                                journal_items.append((0, 0, {'account_id': receivalbe.id,
                                                             'credit': amount,
                                                             'partner_id': record.partner_id.id
                                                             }))

                                vals = {
                                    'journal_id': journal_id.id,
                                    "ref": 'Store credit',
                                    "line_ids": journal_items,

                                }
                                journal_entry = journal_entry_obj.create(vals)
                                for items in journal_entry.line_ids:
                                    if items.debit == amount:
                                        move_lines_refund.append(items)
                                    if items.credit == amount:
                                        move_lines.append(items)

                                journal_entry.post()

                                for lines in record.move_id.line_ids:
                                    move_lines.append(lines)


                                for line in move_lines:
                                    if line.account_id.internal_type == 'receivable':
                                        account_move_lines_to_reconcile_invoice |= line

                                account_move_lines_to_reconcile_invoice.filtered(
                                    lambda l: l.reconciled == False).reconcile()

                                refunded_lines = self.env['account.move.line'].search(
                                    [('partner_id', '=', record.partner_id.id),
                                     ('account_id.internal_type', '=', 'receivable')])

                                for lines_refund in refunded_lines:
                                    if lines_refund not in move_lines:
                                        move_lines_refund.append(lines_refund)

                                for line in move_lines_refund:
                                    if line.account_id.internal_type == 'receivable':
                                        account_move_lines_to_reconcile_refund |= line
                                account_move_lines_to_reconcile_refund.filtered(
                                    lambda l: l.reconciled == False).reconcile()

                                if record.partner_id.store_credit > amount:
                                    balance_change = -amount
                                    record.partner_id.store_credit = record.partner_id.store_credit - amount
                                else:
                                    balance_change = -record.partner_id.store_credit
                                    record.partner_id.store_credit = 0
                                ticket_user_line_obj = self.env['store.credit.history']
                                ticket_user_line_obj.create({
                                    'balance_change': balance_change,
                                    'new_balance': record.partner_id.store_credit,
                                    'partner_id': record.partner_id.id,
                                    'user_id': self.env.user.id,
                                })


        return res

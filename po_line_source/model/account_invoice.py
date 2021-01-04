from odoo import models,fields,api


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    source_doc = fields.Char('Source')


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    source_doc = fields.Char('Source')


    def _prepare_invoice_line_from_po_line(self, line):
        res = super(AccountInvoice, self)._prepare_invoice_line_from_po_line(line)
        res['source_doc'] = line.source_doc
        return res

    @api.onchange('purchase_id')
    def purchase_order_change(self):
        self.source_doc = self.purchase_id.origin
        res = super(AccountInvoice, self).purchase_order_change()
        return res

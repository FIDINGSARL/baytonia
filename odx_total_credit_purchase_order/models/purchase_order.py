# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models,api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    credit_amount_total = fields.Float(string='Total Credit',compute='compute_total_credit',store=True)

    @api.depends('invoice_ids.refund_invoice_ids')
    def compute_total_credit(self):
        for record in self:
            if record.invoice_ids and record.invoice_ids:
                for invoice in record.invoice_ids:
                    if invoice.refund_invoice_ids:
                        for credit_note in invoice.refund_invoice_ids:
                            if credit_note.state=='paid':
                                record.credit_amount_total+=credit_note.amount_total



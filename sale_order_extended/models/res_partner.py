from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    repeat_count_eg = fields.Integer("Repeat Count", compute="_compute_repeat_count", store=True)
    total_ordered_amt_eg = fields.Float("Total Amount", compute="_compute_repeat_count", store=True)
    order_eg_ids = fields.One2many('sale.order', 'partner_id', string="Sale Orders")
    invoice_eg_ids = fields.One2many('account.invoice', 'partner_id', string="Invoices")

    @api.depends('order_eg_ids', 'order_eg_ids.state', 'invoice_eg_ids', 'invoice_eg_ids.state')
    @api.multi
    def _compute_repeat_count(self):
        for rec in self:
            rec.repeat_count_eg = len(rec.order_eg_ids.filtered(lambda o: o.state in ['sale', 'done']))
            rec.total_ordered_amt_eg = sum(
                rec.invoice_eg_ids.filtered(lambda i: i.type == 'out_invoice' and i.state == 'paid').mapped(
                    'amount_total'))

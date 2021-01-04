from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    vendor_id = fields.Many2one('res.partner', string='Vendor')
    total_cost = fields.Float('Subtotal Cost' ,compute='compute_total_coast')

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()
        if self.product_id and self.product_id.seller_ids:
            self.vendor_id = self.product_id.seller_ids[0].name
        return res

    @api.multi
    def compute_total_coast(self):
        for line in self:
            line.total_cost = line.product_uom_qty * line.purchase_price



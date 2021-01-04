from  odoo import models,fields,api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    vendor_id = fields.Many2one('res.partner', string='Vendor')

    @api.onchange('product_id')
    def onchange_vendor_id(self):
        if self.product_id:
            seller = self.env['product.supplierinfo'].search(
                [('product_tmpl_id', '=', self.product_id.product_tmpl_id.id)], order='sequence', limit=1)

            self.vendor_id = seller.name.id
        else:
            self.vendor_id = False

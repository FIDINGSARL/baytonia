# -*- coding: utf-8 -*-

from odoo import api, fields, models

class PosOrderLine(models.Model):
    _inherit = "pos.order.line"
    
    po_line_id = fields.Many2one(
        'purchase.order.line',
        string='Purchase Order Line'
    )
    
    def _order_line_fields(self, line, session_id=None):
        res = super(PosOrderLine, self)._order_line_fields(line, session_id)
        browse_product = self.env['product.product'].browse(res[2].get('product_id', False))
        if browse_product and res[2]:
            browse_product.write({
                'total_available_qty': browse_product.total_available_qty - res[2].get('qty'),
                'sale_qty': browse_product.sale_qty + res[2].get('qty'),
                'sale_price_total': browse_product.sale_price_total + res[2].get('price_unit'),
            })
        res[2].update({
            'po_line_id': browse_product.purchase_order_line_id.id,
        })
        return res

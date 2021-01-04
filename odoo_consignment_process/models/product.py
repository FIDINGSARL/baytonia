# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    purchase_order_line_id = fields.Many2one(
        'purchase.order.line',
        string="Purchase Order Line",
        readonly=True,
    )
    picking_id = fields.Many2one(
        'stock.picking',
        string="Consignment Picking",
        readonly=True,
    )
    sale_order_line_ids = fields.Many2many(
        'sale.order.line',
        string="Sale Order Line",
        readonly=True,
    )
    sale_state = fields.Selection(
        selection=[
            ('sold','Sold'),
            ('not_sold','Not Sold'),
        ],
        default="not_sold",
        string='Consignment Status',
        compute="_consignment_sale_state",
        readonly=True,
    )
    total_available_qty = fields.Float(
        string="Total Available Qty",
        readonly=True,
    )
    purchase_qty = fields.Float(
        string="Purchase Qty",
        readonly=True,
    )
    purchase_price = fields.Float(
        string="Purchase Price",
        readonly=True,
    )
    purchase_price_total = fields.Float(
        string="Purchase Subtotal",
        readonly=True,
    )
    sale_qty = fields.Float(
        string="Sale Qty",
        readonly=True,
    )
    sale_price_total = fields.Float(
        string="Sale Subtotal",
        readonly=True,
    )

    @api.depends()
    def _consignment_sale_state(self):
        for rec in self:
            if rec.total_available_qty <= 0.0:
                rec.sale_state = 'sold'
            else:
                rec.sale_state = 'not_sold'

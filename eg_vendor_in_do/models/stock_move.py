from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = "stock.move"

    vendor_id = fields.Many2one(comodel_name="res.partner", string="Vendor", compute="_compute_vendor_id", store=True)
    purchase_order_id = fields.Many2one(related="created_purchase_line_id.order_id", string="Purchase Order",
                                        store=True)

    @api.depends("product_id")
    def _compute_vendor_id(self):
        for rec in self:
            if rec.product_id:
                vendor_id = rec.product_id.seller_ids and rec.product_id.seller_ids[0].name.id or None
                if vendor_id:
                    rec.vendor_id = vendor_id

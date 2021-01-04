from odoo import models
from odoo.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = "stock.move"

    # @api.multi
    # def write(self, vals):
    #     for rec in self:
    #         if rec.state == 'done':
    #             raise ValidationError("You can not edit done stock move")
    #     return super(StockMove, self).write(vals)
    def write(self, vals):
        if 'product_uom_qty' in vals:
            for move in self.filtered(lambda m: m.state == 'done' and m.picking_id):
                if vals['product_uom_qty'] != move.product_uom_qty:
                    raise ValidationError("Something went wrong, qty changing to 0")
        return super(StockMove, self).write(vals)

    # @api.multi
    # def write(self, vals):
    #     move_qty_ids = self.filtered(lambda m: m.quantity_done)
    #     res = super(StockMove, self).write(vals)
    #     if move_qty_ids.filtered(lambda m: not m.quantity_done):
    #         raise ValidationError("Qty can not be changed after done state")
    #     return res

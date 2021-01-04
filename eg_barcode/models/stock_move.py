from odoo import models, api


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.multi
    def _assign_picking(self):
        res = super(StockMove, self)._assign_picking()
        for rec in self:
            picking_barcode_id = self.env['picking.barcode'].search([('picking_id', '=', rec.picking_id.id)], limit=1)
            if picking_barcode_id:
                picking_barcode_id.get_barcode_lines()
        return res

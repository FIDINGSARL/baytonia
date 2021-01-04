from odoo import models, fields, api


class StockPickingReturn(models.TransientModel):
    _inherit = "stock.return.picking"

    def _create_returns(self):
        new_picking, picking_type_id = super(StockPickingReturn, self)._create_returns()
        if self.picking_id:
            self.picking_id.return_picking_ids = [(4, new_picking, 0)]
            self.picking_id.have_return = True

        return new_picking, picking_type_id

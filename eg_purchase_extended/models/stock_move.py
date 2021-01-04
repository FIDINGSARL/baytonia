from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = "stock.move"

    def _recompute_state(self):
        for move in self.filtered(lambda m: m.state not in ['done', 'cancel']):
            if move.reserved_availability == move.product_uom_qty:
                move.state = 'assigned'
            elif move.reserved_availability and move.reserved_availability <= move.product_uom_qty:
                move.state = 'partially_available'
            else:
                if move.procure_method == 'make_to_order' and not move.move_orig_ids:
                    move.state = 'waiting'
                elif move.move_orig_ids and not all(orig.state in ('done', 'cancel') for orig in move.move_orig_ids):
                    move.state = 'waiting'
                else:
                    move.state = 'confirmed'

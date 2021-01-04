from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = "stock.picking"

    delivery_note_eg = fields.Text("Delivery Note")
    return_picking_ids = fields.One2many(comodel_name="stock.picking", string="Return Orders",
                                         inverse_name="return_picking_id")
    return_picking_id = fields.Many2one(comodel_name="stock.picking", copy=False)
    have_return = fields.Boolean(string="Have Return", copy=False)

    @api.multi
    def view_action_for_return_order(self):
        return_picking_ids = self.return_picking_ids
        if return_picking_ids:
            action = self.env.ref('stock.action_picking_tree_all').read()[0]
            if len(return_picking_ids) > 1:
                action['domain'] = [('id', 'in', return_picking_ids.ids)]
            elif return_picking_ids:
                action['views'] = [(self.env.ref('stock.view_picking_form').id, 'form')]
                action['res_id'] = return_picking_ids.id
            return action

    @api.multi
    def cancel_delivery_order(self):
        action = self.env.ref("sale_stock_extended.action_cancel_warning_wizard").read()[0]
        return action

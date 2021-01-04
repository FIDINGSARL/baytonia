from odoo import models, api


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def button_validate(self):
        auth_required = False
        for rec in self:
            for move in rec.move_lines:
                if move.product_id.type == 'product' and move.product_id.qty_available < move.quantity_done:
                    auth_required = True
                    break
        if not self._context.get("passed") and self.picking_type_code == 'outgoing' and auth_required:
            group_id = self.env.ref('eg_inventory_user_validation.group_validate_picking')
            if self.env.user.id not in group_id.users.ids:
                action = self.env.ref('eg_inventory_user_validation.action_approve_stock_picking_wizard_view').read()[0]
                ctx = dict(self._context)
                ctx.update({'data_id': self.id})
                action.update({"context": ctx})
                return action
        res = super(StockPicking, self).button_validate()
        return res

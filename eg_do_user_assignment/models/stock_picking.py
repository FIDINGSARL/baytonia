from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = "stock.picking"

    responsible_id = fields.Many2one(comodel_name="res.users", string="Responsible Person")
    fully_reserved = fields.Boolean(string="Fully Reserved", compute="_fully_reserved_compute", store=True)
    partial_reserved = fields.Boolean(string="Partial Reserved", compute="_fully_reserved_compute", store=True)

    @api.depends("move_lines", "move_lines.product_uom_qty", 'move_lines.reserved_availability',
                 'state')
    def _fully_reserved_compute(self):
        for rec in self:
            if rec.state in ["done", "cancel"]:
                rec.fully_reserved = False
                rec.partial_reserved = False
                continue
            elif rec.move_lines:
                reserved = False
                partial = False
                total_initial_qty = sum(rec.move_lines.mapped('product_uom_qty'))
                total_reserved_qty = sum(rec.move_lines.mapped('reserved_availability'))
                if total_initial_qty == total_reserved_qty:
                    reserved = True
                elif total_reserved_qty and total_initial_qty > total_reserved_qty:
                    partial = True

                rec.fully_reserved = reserved
                rec.partial_reserved = partial

from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = "stock.picking"

    partner_ids = fields.Many2many(comodel_name="res.partner", string="Suppliers")

    @api.multi
    def set_suppliers(self):
        for rec in self:
            if rec.move_lines:
                vendor_list = []
                for move_id in rec.move_lines:
                    if move_id.state == "waiting" and move_id.product_id.seller_ids:
                        vendor_list.append(move_id.product_id.seller_ids[0].name.id)
                if vendor_list:
                    rec.write({"partner_ids": [(6, 0, vendor_list)]})

    def action_assign(self):
        self.set_suppliers()
        return super(StockPicking, self).action_assign()

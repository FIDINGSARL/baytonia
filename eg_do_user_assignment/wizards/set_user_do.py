from odoo import models, fields, api


class SetUserDo(models.TransientModel):
    _name = "set.user.do"

    stock_picking_ids = fields.Many2many(comodel_name="stock.picking", string="Delivery Order")
    user_id = fields.Many2one(comodel_name="res.users", string="User")

    @api.multi
    def set_user_do(self):
        if self.stock_picking_ids and self.user_id:
            self.stock_picking_ids.write({"responsible_id": self.user_id.id})

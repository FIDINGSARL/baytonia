from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = "stock.picking"

    confirm_person_id = fields.Many2one(comodel_name="res.users", string="Confirm Person By")

    @api.multi
    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        self.confirm_person_id = self.env.user.id
        return res

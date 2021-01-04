from odoo import models, api
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def write(self, vals):
        done_canceled_ids = self.filtered(lambda m: m.state in ["done", "cancel"])
        res = super(StockPicking, self).write(vals)
        if done_canceled_ids.filtered(lambda m: m.state not in ["done", "cancel"]):
            raise ValidationError("State can not be change after done state")
        return res

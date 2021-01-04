from odoo import models, api


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def regenerate_delivery_label(self):
        res = super(StockPicking, self).regenerate_delivery_label()
        if self.carrier_id.delivery_type == "fastlo_delivery":
            self.carrier_id.get_clex_label([self.carrier_tracking_ref], self)
        return res

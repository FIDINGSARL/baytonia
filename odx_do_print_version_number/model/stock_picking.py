from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    report_version_number = fields.Integer('Version Number',default=0)

    @api.multi
    def action_done(self):
        result = super(StockPicking, self).action_done()
        for delivery in self:
            delivery.responsible_id = self.env.user
        return result


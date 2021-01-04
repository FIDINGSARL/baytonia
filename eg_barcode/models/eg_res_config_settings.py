from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    _description = 'Eg Barcode Configuration'

    auto_populated_done_qty = fields.Boolean(string="Auto Populated Done Qty", default=True)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            auto_populated_done_qty=self.env['ir.config_parameter'].sudo().get_param(
                'eg_barcode.auto_populated_done_qty'),
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()

        auto_populated_done_qty = self.auto_populated_done_qty or False

        param.set_param('eg_barcode.auto_populated_done_qty', auto_populated_done_qty)

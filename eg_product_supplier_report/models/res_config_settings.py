from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    email_id = fields.Char(string="Email")

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        icpSudo = self.env['ir.config_parameter'].sudo()   # it is given all access
        res.update(
            email_id=icpSudo.get_param('eg_product_supplier_report.email_id', default=""))

        return res

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        icpSudo = self.env['ir.config_parameter'].sudo()
        icpSudo.set_param("eg_product_supplier_report.email_id", self.email_id)
        return res

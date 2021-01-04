from odoo import models, fields, api


class MoyasarConfiguration(models.Model):
    _name = "moyasar.configuration"

    name = fields.Char(string="Name")
    test_sk = fields.Char(string="Test Secret Key")
    test_pk = fields.Char(string="Test Publishable Key")
    live_sk = fields.Char(string="Live Secret Key")
    live_pk = fields.Char(string="Live Publishable Key")
    callback_url = fields.Char(string="Callback URL")
    currency = fields.Selection([("SAR", "SAR"), ("CAD", "CAD"), ("USD", "USD")], string="Currency Type")
    active = fields.Boolean(string="Active", default=True)
    prod_environment = fields.Boolean(string="Production")

    @api.multi
    def change_environment(self):
        for rec in self:
            rec.prod_environment = not rec.prod_environment

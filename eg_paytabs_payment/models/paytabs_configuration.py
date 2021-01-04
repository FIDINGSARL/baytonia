from odoo import models, fields, api


class PayTabsConfiguration(models.Model):
    _name = "paytabs.configuration"

    email = fields.Char(string="Email", default="mkt@baytonia.com")
    secret_key = fields.Char(string="Secret Key",
                             default="2FFXhg30eMELcNWXCplx36JewEP62Bu4ga2yr5yGRds40p2DOoaSuU60zV6BxBGOMImeNVVF8nJ9MMMBaXtESAFrwL33nJSasepg")
    site_url = fields.Char(string="Site URL", default="https://www.baytonia.com")
    return_url = fields.Char(string="Return URL", default="https://www.baytonia.com/return")
    name = fields.Char(string="Name", default="Paytabs Payment")
    active = fields.Boolean(string="Active", default=True)

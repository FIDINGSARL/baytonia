from odoo import models, fields


class AccountTax(models.Model):
    _inherit = "account.tax"

    default_tax = fields.Boolean(string="Default Tax", help="For sale order")

from odoo import models, fields


class ProductProduct(models.Model):
    _inherit = "product.product"

    exclude_from_report = fields.Boolean(string="Exclude From Report")

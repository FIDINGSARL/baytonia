from odoo import models, fields


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    note = fields.Text(string="Note")

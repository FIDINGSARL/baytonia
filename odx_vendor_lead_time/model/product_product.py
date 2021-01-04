from odoo import models,fields

class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'

    supplier_type = fields.Selection([('local', 'Local'), ('global', 'Global')],related='name.supplier_type', string="Supplier Type")

from odoo import fields, models, api



class ProductProduct(models.Model):
    _inherit = "product.product"

    is_store_credit = fields.Boolean("Store Credit Product")
from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    product_cost_price_eg = fields.Float("Product Cost Price")

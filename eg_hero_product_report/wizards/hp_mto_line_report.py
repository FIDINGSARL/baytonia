from odoo import models, fields


class HpMtoLineReport(models.TransientModel):
    _name = 'hp.mto.line'
    _description = 'Hp mto Line Report'

    serial_no = fields.Integer(string="Serial No.")
    product_id = fields.Many2one('product.product', string="Product")
    image_small = fields.Binary(string="Image")
    qty_available = fields.Integer(string="Quantity")
    category = fields.Char(string="Category")

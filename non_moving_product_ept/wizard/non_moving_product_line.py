from odoo import fields, api, models


class NonMovingProductLine(models.TransientModel):
    _name = 'non.moving.product.line'

    product_id = fields.Many2one('product.product', string='Product')
    default_code = fields.Char(string='Product Code')
    name = fields.Char(string='Product Name')
    qty_available = fields.Integer(string="Available Qty")
    rack_location = fields.Char(string='Rack Location')
    last_sale_date = fields.Date(string="Last Sale Date")
    last_day_oldest = fields.Integer(string="Duration from Last sale(In Days)")
    days_lpd = fields.Integer(string="Days (Last Purchase Date)") # TODO: New Change
    last_purchase_date = fields.Date(string="Last Purchase Date")
    cost_of_product = fields.Float(string="Unit Cost")
    total_cost = fields.Float(string="Total Cost")
    sales_price = fields.Float(string="Sales Price")
    total_sales_price = fields.Float(string="Total Sales Price")
    sales_of_duration = fields.Float(string="Sales Of Duration") # TODO: New Change
    total_sales = fields.Float(string="Total Sales")  # TODO: New Change
    image_small = fields.Binary('Image')
    warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")

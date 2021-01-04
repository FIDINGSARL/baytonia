from odoo import models, api, fields


class VendorProductSalesLineReport(models.TransientModel):
    _name = 'vendor.product.sales.line'
    _description = 'Vendor Product Sales Line Report'

    sale_order_id = fields.Many2one('sale.order', string='Sale Order')
    picking_id = fields.Many2one('stock.picking', string='Delivery Order')
    product_id = fields.Many2one('product.product', string='Product')
    cost_price = fields.Float(string='Cost Price')
    sale_price = fields.Float(string='Selling Price')
    total_sold = fields.Float(string='Total Sold')
    total_cost = fields.Float(string='Total Cost')
    profit = fields.Float(string='Profit')
    image_small = fields.Binary(string="Image")
    is_return = fields.Boolean(string="Return")
    vendor_id = fields.Many2one('res.partner', string="Vendor")
    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")


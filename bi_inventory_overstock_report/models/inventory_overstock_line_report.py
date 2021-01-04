from odoo import models, api, fields


class InventoryOverstockLine(models.TransientModel):
    _name = 'inventory.overstock.line'
    _description = 'Inventory Overstock Line'

    product_id = fields.Many2one('product.product', string="Product")
    qty_available = fields.Integer(string="Current Stock")
    incoming_qty = fields.Integer(string="Incoming Stock")
    outgoing_qty = fields.Integer(string="Outgoing Stock")
    on_hand_qty = fields.Integer(string="Net On Hand Stock")
    sales_count = fields.Integer(string="Sales In Last Days")
    avg_daily_sale = fields.Float(sting="Average Daily Sales")
    recent_purchase_date = fields.Date(string="Recent Purchase Date")
    recent_purchase_qty = fields.Integer(string="Recent Purchase Qty")
    recent_purchase_cost = fields.Float(string="Recent Purchase Cost")
    vendor = fields.Many2one('res.partner', string='Vendor')
    stock_coverage = fields.Integer(string="Stock Coverage")
    expected_stock = fields.Integer(string="Expected Stock")
    overstock_qty = fields.Integer(string="Overstock Qty")
    overstock_value = fields.Float(string="Overstock Value")
    image_small = fields.Binary(string="Image")
    past_date = fields.Date(string="Last Sale Duration")
    advance_date = fields.Date(string="Advance Stock Duration")

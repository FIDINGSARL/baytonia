from odoo import models, fields


class HpMtoLineReport(models.TransientModel):
    _name = 'hp.stock.line'
    _description = 'Hp Stock Line Report'

    serial_no = fields.Integer(string="Serial No.")
    product_id = fields.Many2one('product.product', string="Product")
    image_small = fields.Binary(string="Image")
    days_since_creation = fields.Integer(string="Days Since Creation", help="Total days from since product create")
    qty_available = fields.Integer(string="QTY On Hand", help="Quantity available of Product")
    vendor = fields.Many2one(comodel_name="res.partner", string="Vendor")
    qty_sold = fields.Integer(string="QTY Sold", help="Total product sale quantity of given duration")
    revenue = fields.Float(string="Revenue", help="revenue = qty_sold * sale_price")
    frequency_of_sale = fields.Integer(string="Of sales during period",
                                       help="Total sale order of product for given duration")
    total_out = fields.Float(string="Total Out (%)",
                             help="total_out = (total delivered (duration) * 100) / total delivered (since product create)")
    total_in = fields.Float(string="Total In (%)")
    total_out_scd = fields.Integer(string="Total Out (Since Create Date)",
                                   help="Total delivered quantity of since product create")
    total_in_scd = fields.Integer(string="Total In (Since Create Date)",
                                  help="Total received quantity of since product create")
    total_out_in = fields.Float(string="Total Out/In", help="total_out_in = total_out / total_in")
    lst_price = fields.Float(string="Sale Price")
    standard_price = fields.Float(string="Cost Price")
    total_cost = fields.Float(string="Total Cost")
    profit = fields.Float(string="Profit")
    make_to_order = fields.Char(string="Make to Order")
    category = fields.Char(string="Category")
    average_sale_price = fields.Char(string="Average Sale Price")
    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")
    avg_sale_day = fields.Float(string="Last Cycle Sales / Day")
    avg_revenue_day = fields.Float(string='Avg Revenue/Day')
    max_sale_day = fields.Float(string='Max Sales /Day')
    min_sale_day = fields.Float(string='Min Sales /Day')
    total_avg_sale_price = fields.Float(string='Avg Sale Price * QTY Sold')

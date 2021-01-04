from odoo import api, fields, models, tools


class report_top_growing_product_ept(models.Model):
    # Private attributes
    _name = "report.top.growing.product.ept"
    _description = "Top Growing Products"
    _rec_name = "product_id"
    _auto = False

    # Fields declaration
    default_code = fields.Char("Product Code", help="Product Code")
    product_id = fields.Many2one('product.product', string="Product", index=True, help="Product")
    categ_id = fields.Many2one('product.category', string="Product Cateory", index=True)
    average_sale_price = fields.Float("Average Sale Price", help="Average Sale Price", default=0.0)
    average_cost_price = fields.Float("Average Cost Price", help="Average Cost Price", default=0.0)
    current_stock = fields.Float("Current Stock", help="Current Stock", default=0.0)
    total_sale = fields.Float("Total Sales", help="Total Sales", default=0.0)
    total_purchase = fields.Float("Total Purchase", help="Total Purchase", default=0.0)
    average_sale = fields.Float("Average Sale", help="Average Sale", default=0.0)
    growth_ratio = fields.Float("Growth Ratio", help="Growth Ratio", default=0.0)
    current_period_sales = fields.Float("Current Period Sales", help="Current Period Sales", default=0.0)
    past_period_sales = fields.Float("Past Period Sales", help="Past Period Sales", default=0.0)
    
    
    def get_top_growing_product_report(self,query):
        tools.drop_view_if_exists(self.env.cr, self._table)
        request = """
            CREATE OR REPLACE VIEW %s AS (%s)
        """ % (self._table,query)
        #print(request)
        reuslt=self.env.cr.execute(request)
        return True
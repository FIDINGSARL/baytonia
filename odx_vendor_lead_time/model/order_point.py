from odoo import fields, models, api


class Orderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    @api.onchange('product_id')
    def onchange_product_id(self):
        res = super(Orderpoint, self).onchange_product_id()
        if self.product_id:
            if self.product_id.seller_ids:
                vendor = self.product_id.seller_ids[0]
                if vendor.name:
                    self.lead_days = vendor.name.lead_time
        return res

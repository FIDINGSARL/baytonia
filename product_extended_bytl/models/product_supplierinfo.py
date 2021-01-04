from odoo import models, fields, api


class SupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    @api.multi
    @api.onchange('name','product_id')
    def onchange_product_id(self):
        """
        for variants products (rugs)  price = cost
        @author: JB
        @date: 15-FEB-2019
        """
        self.ensure_one()
        if self.product_id:
            self.price = self.product_id.standard_price
        elif self.product_tmpl_id:
            self.price = self.product_tmpl_id.standard_price

    @api.multi
    def update_variant_product_price_cron(self):
        """
        for variants products (rugs)  price = cost
        @author: JB
        @date: 15-FEB-2019
        """
        for record in self.search([]):
            if record.product_id:
                record.price = record.product_id.standard_price
            elif record.product_tmpl_id:
                record.price = record.product_tmpl_id.standard_price


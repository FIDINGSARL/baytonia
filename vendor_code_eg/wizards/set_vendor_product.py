from odoo import models, fields, api
from odoo.exceptions import Warning


class SetVendorProduct(models.TransientModel):
    _name = "set.vendor.product"

    product_ids = fields.Many2many(comodel_name="product.product", string="Product")
    partner_id = fields.Many2one(comodel_name="res.partner", string="Vendor")
    route_ids = fields.Many2many(comodel_name="stock.location.route", string="Routes")

    @api.multi
    def set_vendor_product(self):
        if self.product_ids and self.partner_id and self.route_ids:
            raise Warning("Vendor and Routes both can not be set at a time, set any one at a time.")

        if self.product_ids and self.partner_id:
            for product_id in self.product_ids:
                product_supplier_id = self.env["product.supplierinfo"].search(
                    [("product_tmpl_id", "=", product_id.product_tmpl_id.id)])
                if product_supplier_id:
                    product_supplier_id.unlink()
                product_supplier_id = self.env["product.supplierinfo"].create(
                    {"product_tmpl_id": product_id.product_tmpl_id.id,
                     "name": self.partner_id.id})
                break
        elif self.product_ids and self.route_ids:
            for product_id in self.product_ids:
                product_id.write({"route_ids": [(6, 0, self.route_ids.ids)]})

from odoo import models, api


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def create(self, vals):
        res = super(ProductProduct, self).create(vals)
        if res.default_code:
            vendor_code = res.default_code.split("-")
            if vendor_code:
                vendor_code = vendor_code[0]
            else:
                return res
            partner_id = self.env["res.partner"].search([("vendor_code", "=", vendor_code)])
            if partner_id:
                product_supplier_id = self.env["product.supplierinfo"].search(
                    [("product_tmpl_id", "=", res.product_tmpl_id.id), ("name", "=", partner_id.id)])
                if not product_supplier_id:
                    product_supplier_id = self.env["product.supplierinfo"].create(
                        {"product_tmpl_id": res.product_tmpl_id.id,
                         "name": partner_id.id})
                    if partner_id.route_ids:
                        res.product_tmpl_id.write({"route_ids": [(6, 0, partner_id.route_ids.ids)]})
        return res

    @api.multi
    def write(self, vals):
        res = super(ProductProduct, self).write(vals)
        if vals.get("default_code"):
            vendor_code = self.default_code.split("-")
            if vendor_code:
                vendor_code = vendor_code[0]
            else:
                return res
            partner_id = self.env["res.partner"].search([("vendor_code", "=", vendor_code)])
            if partner_id:
                product_supplier_id = self.env["product.supplierinfo"].search(
                    [("product_tmpl_id", "=", self.product_tmpl_id.id), ("name", "=", partner_id.id)])
                not_same_supplier_ids = self.env["product.supplierinfo"].search(
                    [("product_tmpl_id", "=", self.product_tmpl_id.id), ("name", "!=", partner_id.id)])
                not_same_supplier_ids.unlink()
                if not product_supplier_id:
                    product_supplier_id = self.env["product.supplierinfo"].create(
                        {"product_tmpl_id": self.product_tmpl_id.id,
                         "name": partner_id.id})
                    if partner_id.route_ids:
                        self.product_tmpl_id.write({"route_ids": [(6, 0, partner_id.route_ids.ids)]})
        return res

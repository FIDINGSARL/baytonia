from odoo import models, api
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.constrains("default_code")
    def _constraint_unique_default_code(self):
        for rec in self:
            if rec.default_code:
                product_id = self.env["product.product"].search(
                    [('id', '!=', rec.id), ('default_code', '=', rec.default_code)])
                if product_id:
                    raise ValidationError(
                        "Product with \"{}\" internal reference already exist!!!".format(product_id.default_code))


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.constrains("default_code")
    def _constraint_unique_default_code_product_template(self):
        for rec in self:
            if rec.default_code:
                product_id = self.env["product.template"].search(
                    [('id', '!=', rec.id), ('default_code', '=', rec.default_code)])
                if product_id:
                    raise ValidationError(
                        "Product with \"{}\" internal reference already exist!!!".format(product_id.default_code))

from odoo import models, api
from odoo.exceptions import AccessError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def create(self, vals):
        res = super(ProductTemplate, self).create(vals)
        group_id = self.env.ref('eg_restrict_product_creation.group_product_create')
        if self.env.user.id not in group_id.users.ids and self.env.user.id != 1:
            raise AccessError("You do not have rights to create product!\nOnly {} Can create Vendors.".format(
                group_id.users.mapped("name")))
        return res


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def create(self, vals):
        res = super(ProductProduct, self).create(vals)
        group_id = self.env.ref('eg_restrict_product_creation.group_product_create')
        if self.env.user.id not in group_id.users.ids and self.env.user.id != 1:
            raise AccessError("You do not have rights to create product!\nOnly {} Can create Vendors.".format(
                group_id.users.mapped("name")))
        return res

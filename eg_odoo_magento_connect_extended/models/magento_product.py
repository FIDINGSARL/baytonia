from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MagentoProduct(models.Model):
    _inherit = "magento.product"

    product_quantity = fields.Float(string="Product Quantity", store=True)

    @api.constrains("mag_product_id")
    def _constraint_unique_mag_product_id(self):
        for rec in self:
            if rec.mag_product_id:
                product_id = self.env["magento.product"].search(
                    [('id', '!=', rec.id), ('mag_product_id', '=', rec.mag_product_id)])
                if product_id:
                    raise ValidationError(
                        "Product with \"{}\" magento id already exist!!!".format(product_id.mag_product_id))


class MagentoProductTemplate(models.Model):
    _inherit = "magento.product.template"

    @api.constrains("mage_product_id")
    def _constraint_unique_mage_product_id(self):
        for rec in self:
            if rec.mage_product_id:
                product_id = self.env["magento.product.template"].search(
                    [('id', '!=', rec.id), ('mage_product_id', '=', rec.mage_product_id)])
                if product_id:
                    raise ValidationError(
                        "Product template with \"{}\" magento id already exist!!!".format(product_id.mage_product_id))

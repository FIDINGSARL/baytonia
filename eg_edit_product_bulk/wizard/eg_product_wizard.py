from odoo import models, fields, api


class EgProductWizard(models.TransientModel):
    _name = "eg.product.wizard"

    product_ids = fields.Many2many(comodel_name="product.template", string="Product")
    sale_ok = fields.Boolean(string="Can be Sold")

    @api.multi
    def save_wizard_data(self):
        self.product_ids.write({'sale_ok': self.sale_ok})

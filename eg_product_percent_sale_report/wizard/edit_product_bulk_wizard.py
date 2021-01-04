from odoo import models, fields, api


class EditProductBulkWizard(models.TransientModel):
    _name = "edit.product.bulk.wizard"

    product_variant_ids = fields.Many2many(comodel_name="product.product", string="Product Variant")
    exclude_from_report = fields.Boolean(string="Exclude From Report")

    @api.multi
    def save_wizard_data(self):
        self.product_variant_ids.write({'exclude_from_report': self.exclude_from_report})
        action = self.env.ref('eg_product_percent_sale_report.launch_product_percent_sale_report_wizard').read([])[0]
        return action

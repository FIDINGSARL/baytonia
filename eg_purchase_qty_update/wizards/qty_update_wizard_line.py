from odoo import fields, models


class QtyUpdateWizardLine(models.TransientModel):
    _name = 'qty.update.wizard.line'
    _description = 'Update Quantity and Price wizard'

    wizard_id = fields.Many2one(comodel_name='qty.update.wizard')
    product_id = fields.Many2one(comodel_name='product.product', string="Product")
    product_qty = fields.Float(string="Quantity")
    order_line_id = fields.Many2one(comodel_name='purchase.order.line')
    price_unit = fields.Float(string="Unit Price")


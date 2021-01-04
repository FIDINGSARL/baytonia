from odoo import fields, models


class EgQtyUpdateWizardLine(models.TransientModel):
    _name = 'eg.qty.update.wizard.line'
    _description = 'Update Quantity wizard'

    wizard_id = fields.Many2one(comodel_name='eg.qty.update.wizard')
    product_id = fields.Many2one(comodel_name='product.product', string="Product")
    product_uom_qty = fields.Float(string="Initial Demand")
    reserved_availability = fields.Float(string="Reserved")
    quantity_done = fields.Float(string="Done")
    move_id = fields.Many2one(comodel_name='stock.move')


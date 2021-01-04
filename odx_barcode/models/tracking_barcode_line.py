from odoo import fields, models, api


class TrackingBarcodeLine(models.Model):
    _name = 'tracking.barcode.line'
    _description = 'Tracking Barcode Line'

    barcode_id = fields.Many2one(comodel_name='tracking.barcode')
    product_id = fields.Many2one(comodel_name='product.product', string="Product")
    product_uom_qty = fields.Float(string="Initial Demand")
    reserved_availability = fields.Float(string="Quantity Reserved")
    quantity_done = fields.Float(string="Quantity Done")
    move_id = fields.Many2one(comodel_name='stock.move')

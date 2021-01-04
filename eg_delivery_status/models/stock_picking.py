from odoo import fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    delivery_status_id = fields.Many2one('stock.picking.status', string="Delivery Status")



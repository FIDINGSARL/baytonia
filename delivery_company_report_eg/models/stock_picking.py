from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    boxes = fields.Integer("No Of Boxes", default=1)

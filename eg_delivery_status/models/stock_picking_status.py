from odoo import fields, models


class StockPickingStatus(models.Model):
    _name = 'stock.picking.status'

    name = fields.Char(string="Delivery Status")

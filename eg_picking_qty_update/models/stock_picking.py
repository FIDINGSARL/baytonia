from odoo import models, fields


class StockPicking(models.Model):
    _inherit = "stock.picking"

    update_process = fields.Boolean("Update Process?")

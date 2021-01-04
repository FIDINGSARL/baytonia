from odoo import models, fields, api
import logging

_logger = logging.getLogger("=== Delivery Order ===")


class StockPicking(models.Model):
    _inherit = "stock.picking"

    return_accepted = fields.Boolean(string="Return Accepted")

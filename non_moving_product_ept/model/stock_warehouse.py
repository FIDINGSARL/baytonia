from odoo import models, fields, api


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    default_non_moving = fields.Boolean(string="Default Non Moving",
                                        help="if mark true so used in weekly send report of non moving product report")

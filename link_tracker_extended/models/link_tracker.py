from odoo import models, fields


class LinkTracker(models.Model):
    _inherit = "link.tracker"

    sale_id = fields.Many2one("sale.order", "Sale Order")

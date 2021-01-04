from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = "sale.order"

    delivery_note_eg = fields.Text("Delivery Note")

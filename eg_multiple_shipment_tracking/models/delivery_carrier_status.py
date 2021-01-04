from odoo import fields, models


class DeliveryStatus(models.Model):
    _name = "delivery.carrier.status"

    name = fields.Char(string="name")
    is_last_status = fields.Boolean(string="Last Status")

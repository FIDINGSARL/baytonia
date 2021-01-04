from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    moyasar_payment_id = fields.Char(string="Payment ID")
    # moyasar_status = fields.Char(string="Moyasar Status")

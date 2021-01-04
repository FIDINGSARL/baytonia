from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    is_delivered = fields.Boolean("Is Delivered ?", readonly=True)
    # payment_gateway_id = fields.Many2one("woo.payment.gateway", "Payment Gateway")
    return_carrier_id = fields.Many2one("delivery.carrier", string="Return Carrier")
    return_tracking_ref = fields.Char("Return Tracking ref")
    return_label_attachment_id = fields.Many2one("ir.attachment")

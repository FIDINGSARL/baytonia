from odoo import models, fields


class SmsInstance(models.Model):
    _inherit = "sms.instance"

    return_disclaimer_msg = fields.Text(string="Return Disclaimer Msg",
                                        help="{{order_number}} == Order Number, {{customer_name}} == Customer Name, {{total_amount}} == Total Amount of Order, {{return_approve_url}} == URL for customer to open ")

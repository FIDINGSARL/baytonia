from odoo import models, fields


class SmsInstance(models.Model):
    _inherit = "sms.instance"

    moyasar_message = fields.Text(string="Moyasar Message",
                                  help="{{moyasar_url}} == Moyasar URL, {{order_number}} == Sale Order")

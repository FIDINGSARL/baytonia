from odoo import models, fields


class SmsInstance(models.Model):
    _inherit = "sms.instance"

    paytabs_message = fields.Text(string="PayTabs Message", help="Use {{paytabs_url}} For URL message")

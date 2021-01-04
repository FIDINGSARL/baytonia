from odoo import models, fields


class SmsInstance(models.Model):
    _inherit = "sms.instance"

    store_credit_message = fields.Text(string="Store Credit Message", help="Use {{name}} For name,{{credit}} for store credit amount and {{credit_total}} for total ")

from odoo import models, fields, api


class SmsInstance(models.Model):
    _inherit = "sms.instance"

    cod_order_msg = fields.Text(string="COD Order Msg",
                                help="This is order {{order_number}} == Order Number, {{url}} == URL")
    bank_msg = fields.Text(string="Bank Msg",
                           help="This is order {{order_number}} == Order Number, {{magento_order_amount}} == Magento Order Amount")

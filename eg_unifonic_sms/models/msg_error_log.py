from odoo import models, fields, api


class MsgErrorLog(models.Model):
    _inherit = "msg.error.log"

    order_detail = fields.Text(string="Order Detail")

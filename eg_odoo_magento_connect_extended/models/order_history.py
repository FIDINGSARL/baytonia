from datetime import datetime

from odoo import models, fields, api


class OrderHistory(models.Model):
    _name = "order.history"

    @api.model
    def set_date(self):
        return datetime.now()

    text = fields.Text(string="Message", readonly=True)
    process = fields.Selection([("yes", "Successful"), ("no", "Unsuccessful"), ("partial", "Partial")],
                               string="Process", readonly=True)
    create_date = fields.Datetime(string="Create Date", default=set_date, readonly=True)
    name = fields.Char(string="Name", readonly=True)
    mag_order_id = fields.Integer(string="Magento ID", readonly=True)

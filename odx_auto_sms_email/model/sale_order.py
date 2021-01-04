from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'


    msg_body = fields.Text("Message")


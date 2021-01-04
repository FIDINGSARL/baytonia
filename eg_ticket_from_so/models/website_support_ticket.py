import logging

from odoo import fields, models

_logging = logging.getLogger(__name__)


class WebsiteSupportTicket(models.Model):
    _inherit = 'website.support.ticket'

    sale_order_id = fields.Many2one(comodel_name='sale.order', string='Sale Order', readonly=True)

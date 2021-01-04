from odoo import models, fields


class WebsiteSupportTicket(models.Model):
    _inherit = 'website.support.ticket'

    stock_picking_id = fields.Many2one(comodel_name='stock.picking', readonly=True)

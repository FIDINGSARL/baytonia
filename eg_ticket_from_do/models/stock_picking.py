from datetime import datetime

from odoo import fields, models, api
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    ticket_count = fields.Integer(string='Ticket Count', compute='_compute_ticket_count')
    website_support_ticket_ids = fields.One2many(comodel_name='website.support.ticket', inverse_name='stock_picking_id')

    def create_ticket_booking(self):
        website_support_ticket_obj = self.env['website.support.ticket']

        website_support_ticket_obj.create({
            'subject': self.origin,
            'stock_picking_id': self.id,
            # 'partner_id': self.partner_id.id,
            # 'email': self.partner_id.email,
            'user_id': self.create_uid.id,
        })

    @api.depends('website_support_ticket_ids')
    def _compute_ticket_count(self):
        for record in self:
            record.ticket_count = len(record.website_support_ticket_ids)

    def action_ticket_booking(self):
        action = self.env.ref('website_support.website_support_ticket_action').read()[0]
        if len(self.website_support_ticket_ids) >= 1:
            action['domain'] = [('id', 'in', self.website_support_ticket_ids.ids)]
            return action
        else:
            raise ValidationError('Not Create a Ticket!!!')

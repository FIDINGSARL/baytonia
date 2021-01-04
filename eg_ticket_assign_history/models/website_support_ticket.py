from datetime import datetime

from dateutil import relativedelta

from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class WebsiteSupportTicket(models.Model):
    _inherit = 'website.support.ticket'

    ticket_assign_history_ids = fields.One2many(comodel_name='ticket.assign.history', inverse_name='website_ticket_id')

    @api.model
    def create(self, vals):
        res = super(WebsiteSupportTicket, self).create(vals)
        if res.user_id:
            ticket_assign_history_obj = self.env['ticket.assign.history']
            ticket_assign_history_obj.create({
                'website_ticket_id': res.id,
                'user_id': res.user_id.id,
                'start_date': datetime.now(),
            })
        return res

    def write(self, vals):
        res = super(WebsiteSupportTicket, self).write(vals)
        for rec in self:
            if vals.get('user_id'):
                end_user_id = self.env['ticket.assign.history'].search(
                    [('website_ticket_id', '=', rec.id), ('end_date', '=', False)])
                if end_user_id.start_date:
                    end_date = datetime.strptime(end_user_id.start_date, DEFAULT_SERVER_DATETIME_FORMAT)
                    difference = relativedelta.relativedelta(datetime.now(), end_date)
                    end_user_id.write({
                        'end_date': datetime.now(),
                        # 'duration': difference.minutes / 60,
                    })
                ticket_user_line_obj = self.env['ticket.assign.history']
                ticket_user_line_obj.create({
                    'website_ticket_id': rec.id,
                    'user_id': rec.user_id.id,
                    'start_date': datetime.now(),
                })
        return res

    def unlink(self):
        if self.ticket_assign_history_ids:
            self.ticket_assign_history_ids.unlink()
        return super(WebsiteSupportTicket, self).unlink()

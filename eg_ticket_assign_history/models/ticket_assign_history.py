from datetime import datetime

from dateutil import relativedelta

from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class TicketAssignHistory(models.Model):
    _name = 'ticket.assign.history'

    user_id = fields.Many2one(comodel_name='res.users')
    start_date = fields.Datetime(string="Starting Date")
    end_date = fields.Datetime(string="End Date")
    # months = fields.Integer(string="Months", compute="_compute_duration")
    days = fields.Integer(string="Days", compute="_compute_duration")
    hours = fields.Integer(string="Hours", compute="_compute_duration")
    minutes = fields.Integer(string="Minutes", compute="_compute_duration")
    website_ticket_id = fields.Many2one(comodel_name='website.support.ticket', ondelete='cascade')

    @api.depends('start_date', 'end_date')
    def _compute_duration(self):
        for rec in self:
            if rec.end_date and rec.start_date:
                start_date = datetime.strptime(rec.start_date, DEFAULT_SERVER_DATETIME_FORMAT)
                end_date = datetime.strptime(rec.end_date, DEFAULT_SERVER_DATETIME_FORMAT)
                difference = relativedelta.relativedelta(end_date, start_date)
                days = difference.months * 28
                # rec.months = difference.months
                rec.days = difference.days + days
                rec.hours = difference.hours
                rec.minutes = difference.minutes


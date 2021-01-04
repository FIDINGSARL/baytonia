from datetime import datetime

from dateutil import relativedelta

from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class WebsiteSupportTicket(models.Model):
    _inherit = 'website.support.ticket'

    user_email = fields.Char('User Email')
    ticket_time_line_ids = fields.One2many(comodel_name='ticket.timeline', inverse_name='website_ticket_id',
                                           string="Ticket Timeline")
    state_count = fields.Integer('State count')

    @api.onchange('user_id')
    def _onchange_user_id(self):
        if self.user_id:
            self.user_email = self.user_id.partner_id.email

    @api.onchange('category')
    def _onchange_category(self):
        stages = self.env['user.state'].search([('ticket_category_path_id.category_id.id', '=', self.category.id)])
        if not stages:
            self.state_count = 0
        for stage in stages:
            if stage.stage == 1:
                self.user_id = stage.user_id.id
                self.state = stage.state.id
                self.state_count = 1

    def next_state(self):
        if self.category:
            stages = self.env['user.state'].search([('ticket_category_path_id.category_id.id', '=', self.category.id)])
            for stage in stages:
                if stage.stage == self.state_count + 1:
                    self.user_id = stage.user_id.id
                    self.user_email = self.user_id.partner_id.email
                    self.state = stage.state.id
                    self.state_count += 1
                    break

    @api.model
    def create(self, vals):
        update_rec = super(WebsiteSupportTicket, self).create(vals)
        for ticket in update_rec:
            if ticket.user_id:
                email_template = self.env['ir.model.data'].get_object('website_support',
                                                                      'support_ticket_user_change')
                email_values = email_template.generate_email([ticket.id])[ticket.id]
                email_values['model'] = "website.support.ticket"
                email_values['res_id'] = ticket.id
                assigned_user = self.env['res.users'].browse(int(ticket.user_id))
                email_values['email_to'] = ticket.user_email
                email_values['body_html'] = email_values['body_html'].replace("_user_name_",
                                                                              assigned_user.name if assigned_user.name else '_user_name_')
                email_values['body'] = email_values['body'].replace("_user_name_",
                                                                    assigned_user.name if assigned_user.name else '_user_name_')
                send_mail = self.env['mail.mail'].create(email_values)
                send_mail.send()
            if vals.get('state'):
                ticket_assign_history_obj = self.env['ticket.timeline']
                ticket_assign_history_obj.create({
                    'website_ticket_id': ticket.id,
                    'user_id': ticket.user_id.id if ticket.user_id else '',
                    'start_date': datetime.now(),
                    'state': ticket.state.id
                })
        return update_rec

    @api.multi
    def print_satisfactory_xls_report(self):
        record = self.env['website.support.ticket'].search([], limit=1)
        return self.env.ref('odx_custom_support_ticket.customer_satisfactory_report_xlsx').report_action(record)

    def write(self, vals):
        res = super(WebsiteSupportTicket, self).write(vals)
        for rec in self:
            if vals.get('user_id'):
                end_user_id = self.env['ticket.timeline'].search(
                    [('website_ticket_id', '=', rec.id), ('end_date', '=', False)], order='id desc', limit=1)
                if end_user_id.start_date:
                    end_date = datetime.strptime(end_user_id.start_date, DEFAULT_SERVER_DATETIME_FORMAT)
                    difference = relativedelta.relativedelta(datetime.now(), end_date)
                    end_user_id.write({
                        'end_date': datetime.now(),
                        # 'duration': difference.minutes / 60,
                    })
                ticket_user_line_obj = self.env['ticket.timeline']
                ticket_user_line_obj.create({
                    'website_ticket_id': rec.id,
                    'user_id': rec.user_id.id,
                    'start_date': datetime.now(),
                    'state': rec.state.id if rec.state else ''
                })
            elif vals.get('state'):
                end_user_id = self.env['ticket.timeline'].search(
                    [('website_ticket_id', '=', rec.id), ('end_date', '=', False), ('state', '!=', rec.state.id)],
                    limit=1)
                if end_user_id.start_date:
                    end_date = datetime.strptime(end_user_id.start_date, DEFAULT_SERVER_DATETIME_FORMAT)
                    difference = relativedelta.relativedelta(datetime.now(), end_date)
                    end_user_id.write({
                        'end_date': datetime.now(),
                        # 'duration': difference.minutes / 60,
                    })
                ticket_user_line_obj = self.env['ticket.timeline']
                ticket_user_line_obj.create({
                    'website_ticket_id': rec.id,
                    'user_id': rec.user_id.id if rec.user_id else '',
                    'start_date': datetime.now(),
                    'state': rec.state.id if rec.state else ''
                })
        return res


class TicketTimeline(models.Model):
    _name = 'ticket.timeline'

    user_id = fields.Many2one(comodel_name='res.users')
    start_date = fields.Datetime(string="Starting Date")
    end_date = fields.Datetime(string="End Date")
    duration = fields.Float(string="Duration", compute="_compute_duration")
    website_ticket_id = fields.Many2one(comodel_name='website.support.ticket', ondelete='cascade')
    state = fields.Many2one('website.support.ticket.states', group_expand='_read_group_state',
                            string="State")

    @api.depends('start_date', 'end_date')
    def _compute_duration(self):
        for rec in self:
            if rec.end_date and rec.start_date:
                start_date = datetime.strptime(rec.start_date, DEFAULT_SERVER_DATETIME_FORMAT)
                end_date = datetime.strptime(rec.end_date, DEFAULT_SERVER_DATETIME_FORMAT)
                difference = relativedelta.relativedelta(end_date, start_date)
                days = difference.months * 30
                rec.duration = difference.days + days

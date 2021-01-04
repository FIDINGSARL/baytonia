import base64
from datetime import datetime, date, timedelta
from io import BytesIO

import xlwt

from odoo import models, fields, api


class SupportUserReportWiz(models.TransientModel):
    _name = "support.user.report.wiz"

    date_from = fields.Date('From')
    date_to = fields.Date('To')
    category = fields.Many2many('website.support.ticket.categories', string="Category", track_visibility='onchange')
    user = fields.Many2many('res.users', string="Users", track_visibility='onchange')

    @api.multi
    def print_report_pdf(self):
        data = {'date_from': self.date_from,
                'date_to': self.date_to,
                'category': self.category,
                'user': self.user,
                'wiz_id': self.id
                }

        return self.env.ref('odx_custom_support_ticket.suport_ticket_report_user').report_action(self, data=data)

    @api.multi
    def print_report_xlsx(self):
        data = {'date_from': self.date_from,
                'date_to': self.date_to,
                'wiz_id': self.id}
        return self.env.ref('odx_custom_support_ticket.suport_ticket_report_user_xlsx').report_action(self, data=data)

from odoo import models, fields, api


class CronEmails(models.Model):
    _name = "cron.emails"
    _rec_name = "report_type"

    report_type = fields.Selection([], string="Report Type", required=True)
    emails = fields.Char(string="Emails", required=True, help="test@gmail.com, test1@gmail.com")
    _sql_constraints = [('eg_bigboss_toolbox', 'unique(report_type)', 'Unique Report Type')]

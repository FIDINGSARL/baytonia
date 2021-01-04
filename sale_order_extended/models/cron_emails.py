from odoo import models, fields, api


class CronEmails(models.Model):
    _inherit = "cron.emails"

    report_type = fields.Selection(selection_add=[("issue_line_report", "Issue Line")])

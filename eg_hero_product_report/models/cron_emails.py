from odoo import models, fields


class CronEmails(models.Model):
    _inherit = "cron.emails"

    report_type = fields.Selection(selection_add=[("hp_stock_report", "Hero Product Stock")])

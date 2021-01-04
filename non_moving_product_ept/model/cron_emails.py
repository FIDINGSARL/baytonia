from odoo import models, fields, api


class CronEmails(models.Model):
    _inherit = "cron.emails"

    report_type = fields.Selection(selection_add=[("non_moving_product", "Non Moving Product")])

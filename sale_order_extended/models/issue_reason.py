from odoo import models, fields


class IssueReason(models.Model):
    _name = "issue.reason"

    name = fields.Char(string="Reason", required=True)

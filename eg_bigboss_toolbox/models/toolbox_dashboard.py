from odoo import models, fields


class ToolboxDashboard(models.Model):
    _name = "toolbox.dashboard"

    name = fields.Char(string="Name")
    color = fields.Integer(string="Color")

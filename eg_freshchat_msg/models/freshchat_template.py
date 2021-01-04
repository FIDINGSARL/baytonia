from odoo import models, fields, api


class FreshchatTemplate(models.Model):
    _name = "freshchat.template"

    name = fields.Char(string="Template Name")
    instance_id = fields.Many2one(comodel_name="sms.instance", string="Instance")

from odoo import models, fields, api


class SmsTemplate(models.Model):
    _name = "sms.template"

    model_id = fields.Many2one(comodel_name="ir.model", string="Model")
    instance_id = fields.Many2one(comodel_name="sms.instance", string="SMS Instance")
    body = fields.Text(string="Message", help="{{person_name}} == Person Name, {{ticket_number}} == Ticket Number")
    name = fields.Char(string="Name")

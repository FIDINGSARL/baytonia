from odoo import models, fields, api


class SmsConfiguration(models.Model):
    _name = "sms.instance"

    name = fields.Char(string="Name")
    priority = fields.Integer(string="Priority", default=1)
    delivery_report = fields.Boolean(string="Delivery Report", required=True)
    provider = fields.Selection([], string="Provider")
    active = fields.Boolean(string="Active", default=True)

    # relation

    calling_code_from_id = fields.Many2one(comodel_name="calling.code", string="Calling Code From")
    msg_status_ids = fields.One2many(comodel_name="msg.status", inverse_name="sms_instance_id", string="Msg Status")
    msg_delivery_report_ids = fields.One2many(comodel_name="msg.delivery.report", inverse_name="sms_instance_id",
                                              string="Msg Delivery Report")

    @api.onchange("provider")
    def onchange_provider(self):
        a = None

    @api.multi
    def toggle_active(self):
        for rec in self:
            rec.active = not rec.active

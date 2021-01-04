from odoo import models, fields


class MsgErrorLog(models.Model):
    _name = "msg.error.log"
    _rec_name = "process"

    sms_instance_id = fields.Many2one(comodel_name="sms.instance", string="Sms Instance")
    datetime = fields.Datetime(string="Date Time")
    error_message = fields.Char(string="Error Message")
    process = fields.Char(string="Process")

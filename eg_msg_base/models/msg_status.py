from odoo import models, fields


class MsgStatus(models.Model):
    _name = "msg.status"

    name = fields.Char(string="Status", readonly=True)
    is_last_status = fields.Boolean(string="Is Last Status")
    sms_instance_id = fields.Many2one(comodel_name="sms.instance", string="Sms Instance", readonly=True)

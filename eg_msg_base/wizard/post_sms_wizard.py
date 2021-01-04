from odoo import models, fields, api
from datetime import datetime, date


class PostSmsWizard(models.TransientModel):
    _name = "post.sms.wizard"

    message = fields.Text(string="Message")
    message_datetime = fields.Datetime(string="Message DateTime", default=datetime.now())
    calling_code_id = fields.Many2one(comodel_name="calling.code", string="Calling Code")
    number = fields.Char(string="Number")
    send_msg_to = fields.Selection([("group", "Group"), ("individual_number", "Individual Number")],
                                   string="Send Msg To", default="individual_number")
    group_msg_id = fields.Many2one(comodel_name="group.msg", string="Group Msg")
    message_title = fields.Char(string="Message Title")

    @api.multi
    def post_sms(self):
        current_datetime = datetime.now()
        self.env["msg.error.log"].create({"datetime": current_datetime,
                                          "error_message": "No SMS Instance found for this data",
                                          "process": "Send Msg",
                                          "sms_instance_id": False})

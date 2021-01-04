from odoo import models, fields, api
from requests import request
from datetime import datetime, date
from odoo.exceptions import ValidationError, Warning
import json


class MsgSender(models.Model):
    _name = "msg.sender"

    name = fields.Char(string="Sender ID")

    @api.multi
    def get_sender_id(self):
        current_datetime = datetime.now()
        sms_instance_id = self.env["sms.instance"].search([("provider", "=", "unifonic_sms")])
        if not sms_instance_id:
            raise ValidationError("Please First Create SMS Instance")
        url = "{}/Account/getSenderIDs".format(
            sms_instance_id.live_url) if sms_instance_id.environment else "{}/Account/getSenderIDs".format(
            sms_instance_id.test_url)
        try:
            payload = "AppSid={}".format(sms_instance_id.app_sid)
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            response = request("POST", url=url, data=payload, headers=headers)

        except Exception as e:
            self.env["msg.error.log"].create({"sms_instance_id": sms_instance_id.id,
                                              "datetime": current_datetime,
                                              "error_message": str(e),
                                              "process": "Get Sender ID"})
            response = False
        if response:
            if response.status_code == 200:
                if not sms_instance_id.environment:
                    raise Warning("You can fetch data only for production not for test")

                else:
                    response = json.loads(response.text)
                    if response.get("errorCode") != "ER-00":
                        raise Warning("{}".format(response))
                    for sender_id in response.get("data").get("senderNames"):
                        msg_sender_id = self.search([("name", "=", sender_id.get("SenderID"))])
                        if not msg_sender_id:
                            self.create({"name": sender_id.get("SenderID")})

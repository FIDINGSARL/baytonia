from odoo import models, fields, api
from datetime import datetime, date
from requests import request
import json
import logging

_logger = logging.getLogger("==== Msg Delivery Report (Unifonic message) ====")


class MsgDeliveryReport(models.Model):
    _inherit = "msg.delivery.report"

    message_unit = fields.Integer(string="Message Unit", readonly=True)
    provider = fields.Selection(related="sms_instance_id.provider", readonly=True, store=True, string="provider")

    @api.multi
    def get_status_update(self):
        current_datetime = datetime.now()
        msg_delivery_ids = self.browse(self._context.get("active_ids"))
        for msg_delivery_id in msg_delivery_ids.filtered(lambda l: not l.msg_status_id.is_last_status):
            sms_instance_id = msg_delivery_id.sms_instance_id

            if sms_instance_id.provider == "unifonic_sms":
                url = "{}/Messages/GetMessageIDStatus".format(
                    sms_instance_id.live_url) if sms_instance_id.environment else "{}/Messages/GetMessageIDStatus".format(
                    sms_instance_id.test_url)
                try:
                    payload = "AppSid={}&MessageID={}".format(sms_instance_id.app_sid, msg_delivery_id.sid)
                    headers = {"Content-Type": "application/x-www-form-urlencoded"}
                    response = request("POST", url=url, data=payload, headers=headers)
                except Exception as e:
                    self.env["msg.error.log"].create({"sms_instance_id": sms_instance_id.id,
                                                      "datetime": current_datetime,
                                                      "error_message": str(e),
                                                      "process": "Update Status"})
                    response = None
                if response:
                    if response.status_code == 200:
                        if sms_instance_id.environment:
                            response = json.loads(response.text)
                            if response.get("errorCode") != "ER-00":
                                _logger.info("{} (Status Update)".format(response))
                                self.env["msg.error.log"].create({"sms_instance_id": sms_instance_id.id,
                                                                  "datetime": current_datetime,
                                                                  "process": "Update Status"})
                                return
                            data = response.get("data")
                            status = data.get("Status")
                        else:
                            response = response.text.replace(",\n", "\n")
                            response = response.replace("\n", ",")
                            response = response.replace(",,", "")
                            response = response.replace("{,", "{")
                            response = json.loads(response)
                            status = response.get("Status").capitalize()
                        if not status == msg_delivery_id.msg_status_id.name:
                            status_id = self.env["msg.status"].search(
                                [("name", "=", status),
                                 ("sms_instance_id.provider", "=", sms_instance_id.provider)])
                            if not status_id:
                                status_id = self.env["msg.status"].create(
                                    {"name": status, "sms_instance_id": sms_instance_id.id})
                            msg_delivery_id.write({"msg_status_id": status_id.id})

        return super(MsgDeliveryReport, self).get_status_update()

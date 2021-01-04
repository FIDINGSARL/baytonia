from odoo import models, fields, api
from datetime import datetime, date
from requests import request
import json
import logging

_logger = logging.getLogger("==== Msg Delivery Report (FreshChat Message) ====")


class MsgDeliveryReport(models.Model):
    _inherit = "msg.delivery.report"

    order_id = fields.Many2one(comodel_name="sale.order", string="Sale order", readonly=True)
    provider = fields.Selection(related="sms_instance_id.provider", readonly=True, store=True, string="provider")

    @api.multi
    def get_status_update(self):
        current_datetime = datetime.now()
        msg_delivery_ids = self.browse(self._context.get("active_ids"))
        for msg_delivery_id in msg_delivery_ids.filtered(lambda l: not l.msg_status_id.is_last_status):
            sms_instance_id = msg_delivery_id.sms_instance_id

            if sms_instance_id.provider == "freshchat_sms":
                url = "{}?request_id={}".format(sms_instance_id.fc_url, msg_delivery_id.sid)
                token = "Bearer {}".format(sms_instance_id.fc_token)
                headers = {"Authorization": token,
                           'Content-Type': 'application/json'}
                try:
                    response = request("GET", url=url, headers=headers)
                except Exception as e:
                    self.env["msg.error.log"].create({"sms_instance_id": sms_instance_id.id,
                                                      "datetime": current_datetime,
                                                      "error_message": str(e),
                                                      "process": "Get Status"})

                    response = False
                if response:
                    if response.status_code == 200:
                        response = json.loads(response.text)
                        outbound_messages = response.get("outbound_messages")[0]
                        status = outbound_messages.get("status")
                        if status == "IN_PROGRESS":
                            status = "IN PROGRESS"
                        if not status == msg_delivery_id.msg_status_id.name:
                            status_id = self.env["msg.status"].search(
                                [("name", "=", status),
                                 ("sms_instance_id.provider", "=", sms_instance_id.provider)])
                            if not status_id:
                                status_id = self.env["msg.status"].create(
                                    {"name": status, "sms_instance_id": sms_instance_id.id})
                            msg_delivery_id.write({"msg_status_id": status_id.id})

        return super(MsgDeliveryReport, self).get_status_update()

import ast
import json
import logging
from datetime import datetime
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from odoo import models, api

_logger = logging.getLogger("==== Unifonic Post SMS ====")


class UnifonicPostSmsWizard(models.TransientModel):
    _inherit = "post.sms.wizard"

    @api.multi
    def send_sms(self, msg_delivery_report_id=None, body=None, dst_number=None, msg_record_id=None):
        response_message = ""
        current_datetime = datetime.now()
        sms_instance_id = self.env["sms.instance"].search([("provider", "=", "unifonic_sms")])
        if not sms_instance_id:
            error_message = "Please First Create SMS Instance"
            self.env["msg.error.log"].create({"sms_instance_id": sms_instance_id.id,
                                              "datetime": current_datetime,
                                              "error_message": error_message,
                                              "process": "Send SMS"})
            _logger.info(error_message)
            return
        status = False
        url = "{}/Messages/Send".format(
            sms_instance_id.live_url if sms_instance_id.environment else sms_instance_id.test_url)
        try:
            dst_number = dst_number.lstrip("0")
            dst_number = dst_number.lstrip("+")
            if not dst_number.startswith("966"):
                dst_number = "966{}".format(dst_number)
            # ======================================
            values = urlencode({
                'AppSid': sms_instance_id.app_sid,
                'Recipient': dst_number,
                'Body': body
            }).encode("utf-8")
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            request = Request('http://api.unifonic.com/rest/Messages/Send', data=values, headers=headers)
            # response_without_read = urlopen(request)
            response = urlopen(request)
            # response_encoded = response.decode("utf-8")
            # response = json.dumps(response)
            # print(response_body)
            # ========================================
            # For arabic fix
            # payload = "AppSid={}&Recipient={}&Body={}&SenderID={}".format(sms_instance_id.app_sid, dst_number,
            #                                                               body.encode('utf-8'),
            #                                                               sms_instance_id.sender_id.name)
            # payload = "AppSid={}&Recipient={}&Body={}&SenderID={}".format(sms_instance_id.app_sid, dst_number,
            #                                                               body, sms_instance_id.sender_id.name)
            # headers = {"Content-Type": "application/x-www-form-urlencoded"}
            # response = request("POST", url=url, data=payload, headers=headers)

        except Exception as e:
            if msg_record_id:
                msg_record_id.write({"state": "error"})
            self.env["msg.error.log"].create({"sms_instance_id": sms_instance_id.id,
                                              "datetime": current_datetime,
                                              "error_message": str(e),
                                              "process": "Send SMS"})
            status = "Error"
            response_message = "{}".format(e)
            response = False
        message_id = None
        number_of_units = None
        if response:
            if response.code == 200:
                # if sms_instance_id.environment:
                response_read = response.read()
                _logger.info(response_read)
                response = json.loads(response_read.decode('utf-8'))

                # else:
                #     response_read = response.read()
                #     _logger.info(response_read)
                #     response = json.loads(response_read.decode('utf-8'))
                # response = response.text.replace(",\n", "\n")
                # response = response.replace("\n", ",")
                # response = response.replace(",,", "")
                # response = response.replace("{,", "{")
                # response = ast.literal_eval(response)

                if response.get("errorCode") != "ER-00":
                    if msg_record_id:
                        msg_record_id.write({"state": "error"})
                    status = "Error"
                    _logger.info("{}".format(response))
                    self.env["msg.error.log"].create({"sms_instance_id": sms_instance_id.id,
                                                      "datetime": current_datetime,
                                                      "process": "Send SMS",
                                                      "error_message": "{}".format(response.get("message"))})
                    response_message = "{}".format(response.get("message"))
                else:
                    if msg_record_id:
                        msg_record_id.write({"state": "send"})
                    data = response.get("data")
                    status = data.get("Status").capitalize()
                    message_id = data.get("MessageID")
                    number_of_units = data.get("NumberOfUnits")
                    response_message = "Success"
            else:
                if msg_record_id:
                    msg_record_id.write({"state": "failed"})
                    status = "Error"
                self.env["msg.error.log"].create({"sms_instance_id": sms_instance_id.id,
                                                  "datetime": current_datetime,
                                                  "process": "Send SMS",
                                                  "error_message": "{}".format(response.read().decode('utf-8'))})
                response_message = "{}".format(response.read().decode('utf-8'))

        status_id = self.env["msg.status"].search(
            [("name", "=", status), ("sms_instance_id.provider", "=", sms_instance_id.provider)])

        if not status_id:
            status_id = self.env["msg.status"].create({"name": status, "sms_instance_id": sms_instance_id.id})
        report_values = {"from_number": "By Default",
                         "to_number": dst_number,
                         "body": body,
                         "msg_status_id": status_id.id,
                         "message_datetime": current_datetime,
                         "sms_instance_id": sms_instance_id.id,
                         "sid": message_id,
                         "message_unit": number_of_units and int(number_of_units)}
        if self.send_msg_to == "group":
            report_values.update({"is_child": True,
                                  "is_group": True,
                                  "msg_delivery_report_id": msg_delivery_report_id.id,
                                  "message_title": self.message_title})

        self.env["msg.delivery.report"].create(report_values)
        return response_message

    @api.multi
    def post_sms(self):
        current_datetime = datetime.now()

        if not self._context.get("provider") == "unifonic_sms":
            return super(UnifonicPostSmsWizard, self).post_sms()

        sms_instance_id = self.env["sms.instance"].search([("provider", "=", "unifonic_sms")])
        if not sms_instance_id:
            error_message = "Please First Create SMS Instance"
            self.env["msg.error.log"].create({"sms_instance_id": sms_instance_id.id,
                                              "datetime": current_datetime,
                                              "error_message": error_message,
                                              "process": "Send SMS"})
            _logger.info(error_message)
            return

        number_list = []
        msg_delivery_report_id = self.env["msg.delivery.report"]

        body = self.message
        if self.send_msg_to == "group":
            for number_list_id in self.group_msg_id.number_list_ids:
                to_number = number_list_id.calling_code_id.prefix_number + number_list_id.number
                number_list.append(to_number)
            multiple_number = ",".join(number_list)
            msg_delivery_report_id = self.env["msg.delivery.report"].create({"from_number": "",
                                                                             "to_number": multiple_number,
                                                                             "body": self.message,
                                                                             "msg_status_id": False,
                                                                             "message_datetime": current_datetime,
                                                                             "sid": False,
                                                                             "sms_instance_id": sms_instance_id.id,
                                                                             "is_group": True,
                                                                             "is_parent": True,
                                                                             "message_title": self.message_title})

        else:
            number_list.append(self.number)
        if number_list:
            for number in number_list:
                if self.send_msg_to == "individual_number":
                    if not self.calling_code_id.prefix_number:
                        dst_number = number
                    else:
                        if self.calling_code_id.prefix_number in number:
                            dst_number = number
                        else:
                            dst_number = self.calling_code_id.prefix_number + number
                else:
                    dst_number = number
                self.send_sms(body=body, dst_number=dst_number, msg_delivery_report_id=msg_delivery_report_id)

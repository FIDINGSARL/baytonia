from odoo import models, api, fields
import ast
import json
import logging
from datetime import datetime
from requests import request
from odoo.exceptions import Warning

_logger = logging.getLogger("==== FreshChat Post SMS ====")


class PostSmsWizard(models.TransientModel):
    _inherit = "post.sms.wizard"

    @api.model
    def default_get(self, fields_list):
        res = super(PostSmsWizard, self).default_get(fields_list)
        order_id = self.env["sale.order"].browse(self._context.get("active_id"))
        if order_id:
            if "number" in fields_list:
                number = order_id.partner_id.phone or order_id.partner_id.mobile
                if not number and order_id.partner_invoice_id:
                    number = order_id.partner_invoice_id.phone or order_id.partner_invoice_id.mobile
                if not number and order_id.partner_shipping_id:
                    number = order_id.partner_shipping_id.phone or order_id.partner_shipping_id.mobile
                if not number:
                    res['number'] = number
        return res

    template_id = fields.Many2one(comodel_name="freshchat.template", string="Template")

    @api.multi
    def post_sms(self):
        current_datetime = datetime.now()
        if not self._context.get("provider") == "freshchat_sms":
            return super(PostSmsWizard, self).post_sms()
        if self.send_msg_to == "group":
            raise Warning("Group is not allowed")
        sms_instance_id = self.env["sms.instance"].search([("provider", "=", "freshchat_sms")])
        if not sms_instance_id:
            error_message = "Please First Create SMS Instance"
            self.env["msg.error.log"].create({"sms_instance_id": sms_instance_id.id or None,
                                              "datetime": current_datetime,
                                              "error_message": error_message,
                                              "process": "Send SMS"})
            _logger.info(error_message)
            return
        if not self.message or not self.template_id or not self.number:
            raise Warning("Please fill the all field")

        body = self.message.split(",")
        template_data = []
        for msg in body:
            template_data.append({"data": msg})

        to_number = self.number
        if self.calling_code_id.prefix_number == "+91":
            to_number = "+91{}".format(to_number)
        else:
            to_number = to_number.lstrip("0")
            to_number = to_number.lstrip("+")
            if not to_number.startswith("966"):
                to_number = "+966{}".format(to_number)
        from_number = sms_instance_id.fc_number
        from_number = from_number.lstrip("0")
        from_number = from_number.lstrip("+")
        if not from_number.startswith("966"):
            from_number = "+966{}".format(from_number)

        url = "{}/whatsapp".format(sms_instance_id.fc_url)
        token = "Bearer {}".format(sms_instance_id.fc_token)
        template = self.template_id.name
        data = {"from": {"phone_number": from_number}, "to": [{"phone_number": to_number}], "data": {
            "message_template": {
                "storage": "none",
                "namespace": sms_instance_id.fc_namespace,
                "template_name": template,
                "language": {"policy": "fallback",
                             "code": "en"},
                "template_data": template_data}}}
        headers = {"Authorization": token,
                   'Content-Type': 'application/json'}
        status = None
        try:
            response = request("POST", url=url, headers=headers, data=json.dumps(data))
        except Exception as e:
            self.env["msg.error.log"].create({"sms_instance_id": sms_instance_id.id,
                                              "datetime": current_datetime,
                                              "error_message": str(e),
                                              "process": "Send SMS"})
            status = "Error"
            response = False
        request_id = None
        if response:
            if response.status_code == 202:
                response = json.loads(response.text)
                request_id = response.get("request_id")
                status_url = "{}?request_id={}".format(sms_instance_id.fc_url, request_id)
                try:
                    status_response = request("GET", url=status_url, headers=headers)
                except Exception as e:
                    self.env["msg.error.log"].create({"sms_instance_id": sms_instance_id.id,
                                                      "datetime": current_datetime,
                                                      "error_message": str(e),
                                                      "process": "Get Status"})
                    status = "Error"
                    status_response = False
                if status_response:
                    if status_response.status_code == 200:
                        status_response = json.loads(status_response.text)
                        outbound_messages = status_response.get("outbound_messages")[0]
                        status = outbound_messages.get("status")
                        if status == "IN_PROGRESS":
                            status = "IN PROGRESS"
        status_id = self.env["msg.status"].search(
            [("name", "=", status), ("sms_instance_id.provider", "=", sms_instance_id.provider)])

        if not status_id:
            status_id = self.env["msg.status"].create({"name": status, "sms_instance_id": sms_instance_id.id})
        order_id = self.env["sale.order"].browse(self._context.get("active_id"))
        report_values = {"from_number": from_number,
                         "to_number": to_number,
                         "body": body,
                         "msg_status_id": status_id.id,
                         "message_datetime": current_datetime,
                         "sms_instance_id": sms_instance_id.id,
                         "sid": request_id,
                         "order_id": order_id.id or None}
        self.env["msg.delivery.report"].create(report_values)

    @api.onchange("template_id")
    def onchange_on_template_id(self):
        template_id = self.template_id
        if template_id:
            order_id = self.env["sale.order"].browse(self._context.get("active_id"))
            if template_id.name == "welcome_message":
                self.message = order_id.partner_id.name
            elif template_id.name == "visa_payment":
                self.message = "{},{}".format(order_id.partner_id.name, order_id.name)
            elif template_id.name == "bank_payment":
                self.message = "{},{}".format(order_id.partner_id.name, order_id.name)
        else:
            self.message = ""

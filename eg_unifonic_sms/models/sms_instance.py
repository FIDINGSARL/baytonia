from odoo import models, fields, api
from requests import request
from datetime import datetime, date
import json
import logging

_logger = logging.getLogger("==== SMS Instance (Unifonic message) ====")


class SmsInstance(models.Model):
    _inherit = "sms.instance"

    app_sid = fields.Char(string="App SID")
    provider = fields.Selection(selection_add=[('unifonic_sms', 'Unifonic SMS')])
    test_url = fields.Char(string="Test URL",
                           default="https://private-anon-19e586a7e2-unifonic.apiary-mock.com/rest")
    live_url = fields.Char(string="Live URL", default="https://api.unifonic.com/rest")
    for_draft = fields.Boolean(string="Draft")
    for_sent = fields.Boolean(string="Sent")
    for_sale = fields.Boolean(string="Sale")
    for_done = fields.Boolean(string="Done")
    for_cancel = fields.Boolean(string="Cancel")
    for_tracking_url = fields.Boolean(string="Tracking URL")
    draft_msg = fields.Text(string="Draft msg")
    sent_msg = fields.Text(string="Sent msg")
    sale_msg = fields.Text(string="Sale msg")
    done_msg = fields.Text(string="Done msg")
    cancel_msg = fields.Text(string="Cancel msg")
    tracking_url_msg = fields.Text(string="Tracking URL msg")
    environment = fields.Boolean(string="Environment")
    sender_id = fields.Many2one(comodel_name="msg.sender", string="Sender")
    account_balance = fields.Char(string="Account Balance", readonly=True)
    remaining_msg = fields.Integer(string="Remaining Message", readonly=True)
    marketing_url = fields.Char(string="Marketing URL")

    @api.onchange("for_draft")
    def onchange_for_draft(self):
        if not self.for_draft:
            self.draft_msg = None

    @api.onchange("for_sent")
    def onchange_for_sent(self):
        if not self.for_sent:
            self.sent_msg = None

    @api.onchange("for_sale")
    def onchange_for_sale(self):
        if not self.for_sale:
            self.sale_msg = None

    @api.onchange("for_done")
    def onchange_for_done(self):
        if not self.for_done:
            self.done_msg = None

    @api.onchange("for_cancel")
    def onchange_for_cancel(self):
        if not self.for_cancel:
            self.cancel_msg = None

    @api.onchange("for_tracking_url")
    def onchange_for_tracking_url(self):
        if not self.for_tracking_url:
            self.tracking_url_msg = None

    @api.onchange("provider")
    def onchange_provider(self):
        if not self.name:
            if self.provider:
                if self.provider == "unifonic_sms":
                    self.name = "Unifonic SMS"
                else:
                    super(SmsInstance, self).onchange_provider()
            else:
                self.name = ""

    @api.multi
    def change_environment(self):
        for rec in self:
            rec.environment = not rec.environment

    @api.multi
    def import_sender_id(self):
        return self.env["msg.sender"].get_sender_id()

    @api.multi
    def check_account_balance(self):
        current_datetime = datetime.now()
        sms_instance_id = self.search([("provider", "=", "unifonic_sms")])
        if not sms_instance_id:
            error_message = "Please First Create SMS Instance (Check Balance)"
            self.env["msg.error.log"].create({"sms_instance_id": sms_instance_id.id,
                                              "datetime": current_datetime,
                                              "error_message": error_message,
                                              "process": "Check Account Balance"})
            _logger.info(error_message)

            return
        url = "{}/Account/GetBalance".format(
            sms_instance_id.live_url) if sms_instance_id.environment else "{}/Account/GetBalance".format(
            sms_instance_id.test_url)
        try:
            payload = "AppSid={}".format(sms_instance_id.app_sid)
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            response = request("POST", url=url, data=payload, headers=headers)

        except Exception as e:
            self.env["msg.error.log"].create({"sms_instance_id": sms_instance_id.id,
                                              "datetime": current_datetime,
                                              "error_message": str(e),
                                              "process": "Check Account Balance"})

            response = False
        if response:
            if response.status_code == 200:
                if not sms_instance_id.environment:
                    error_message = "You can fetch data only for production not for test (Check Balance)"
                    self.env["msg.error.log"].create({"sms_instance_id": sms_instance_id.id,
                                                      "datetime": current_datetime,
                                                      "error_message": error_message,
                                                      "process": "Check Account Balance"})
                    _logger.info(error_message)

                else:
                    response = json.loads(response.text)
                    if response.get("errorCode") != "ER-00":
                        self.env["msg.error.log"].create({"sms_instance_id": sms_instance_id.id,
                                                          "datetime": current_datetime,
                                                          "error_message": "{}".format(response.get("message")),
                                                          "process": "Check Account Balance"})
                        _logger.info("{} (Check Balance)".format(response))
                        return

                    sms_instance_id.write({"account_balance": response.get("data").get("Balance")})

    @api.multi
    def check_account_message(self):
        current_datetime = datetime.now()
        sms_instance_id = self.search([("provider", "=", "unifonic_sms")])
        if not sms_instance_id:
            error_message = "Please First Create SMS Instance (Check Message Point)"
            self.env["msg.error.log"].create({"sms_instance_id": sms_instance_id.id,
                                              "datetime": current_datetime,
                                              "error_message": error_message,
                                              "process": "Check Message Point"})
            _logger.info(error_message)

            return
        url = "{}/Account/GetPackagesDetails".format(
            sms_instance_id.live_url) if sms_instance_id.environment else "{}/Account/GetPackagesDetails".format(
            sms_instance_id.test_url)
        try:
            payload = "AppSid={}".format(sms_instance_id.app_sid)
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            response = request("POST", url=url, data=payload, headers=headers)

        except Exception as e:
            self.env["msg.error.log"].create({"sms_instance_id": sms_instance_id.id,
                                              "datetime": current_datetime,
                                              "error_message": str(e),
                                              "process": "Check Message Point"})

            response = False
        if response:
            if response.status_code == 200:
                if not sms_instance_id.environment:
                    error_message = "You can fetch data only for production not for test (Check Message point)"
                    self.env["msg.error.log"].create({"sms_instance_id": sms_instance_id.id,
                                                      "datetime": current_datetime,
                                                      "error_message": error_message,
                                                      "process": "Check Message Point"})
                    _logger.info(error_message)

                else:
                    response = json.loads(response.text)
                    if response.get("errorCode") != "ER-00":
                        self.env["msg.error.log"].create({"sms_instance_id": sms_instance_id.id,
                                                          "datetime": current_datetime,
                                                          "error_message": "{}".format(response.get("message")),
                                                          "process": "Check Message Point"})
                        _logger.info("{} (Check Balance)".format(response))
                        return

                    sms_instance_id.write({"remaining_msg": int(response.get("data")[0].get("RemainingUnits"))})

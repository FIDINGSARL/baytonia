# -*- coding: utf-8 -*-
##############################################################################
#
#    Sahil Navadiya
#    Copyright (C) 2018-TODAY (<navadiyasahil@gmail.com>).
#
##############################################################################

import base64
import logging
from ast import literal_eval
from http import client as client

from openerp.exceptions import ValidationError

from odoo import api, fields, models, _

# from infobip.clients import send_single_textual_sms
# from infobip.api.model.sms.mt.send.textual.SMSTextualRequest import SMSTextualRequest
# from infobip.util.configuration import Configuration
# from __init__ import configuration
_logger = logging.getLogger(__name__)


class InfobipSms(models.Model):
    _name = "fl.infobip.sms"
    _description = "Infobip SMS"

    name = fields.Char("Name", required=True)
    active = fields.Boolean(default=True)
    base_url = fields.Char("Base URL", default="api.infobip.com", required=True)
    # authorization = fields.Char("Authorization Code", default="QWxhZGRpbjpvcGVuIHNlc2FtZQ==", required=True)
    username = fields.Char("Username", required=True)
    password = fields.Char("Password", required=True)
    test_no = fields.Char("Test Number (with country code)")

    @api.multi
    def test_sms_fl(self):
        if self.test_no is False:
            raise ValidationError(_('Please enter valid test number with country code.'))
        test_txt = "Test SMS"
        self.send_sms(test_txt, self.test_no, keep_history=True)

        # conn = client.HTTPSConnection("api.infobip.com")
        # payload = "{\"from\":\"InfoSMS\",\"to\":\"918849778471\",\"text\":\"شحن SMS.\"}"
        # headers = {
        #    'authorization': "Basic YmF5dG9uaWE6MTIzVGVzdCE=",
        #    'content-type': "application/json",
        #    'accept': "application/json"
        #    }
        # conn.request("POST", "/sms/2/text/single", payload, headers)
        # res = conn.getresponse()
        # data = res.read()
        # print(data.decode("utf-8"))

    @api.model
    def create(self, vals):
        if self.env['fl.infobip.sms'].search_count([("active", "=", True)]) > 1:
            raise ValidationError(_(
                'You can have only one active infobip configuration record at once. You can\'t create other one since atleast one active record.'))
        return super(InfobipSms, self).create(vals)

    def send_sms(self, body_text=False, send_to=False, keep_history=True):
        # conn = http.client.HTTPSConnection("api.infobip.com")
        infobip_config = self.env['fl.infobip.sms'].search([], limit=1)
        if infobip_config and infobip_config.base_url and infobip_config.username and infobip_config.password:
            conn = client.HTTPSConnection(infobip_config.base_url)

            payload = "{\"from\":\"InfoSMS\",\"to\":\"%s\",\"text\":\"%s\"}" % (
                send_to, body_text.encode('utf-8').decode('latin-1', 'ignore'))
            data_str = infobip_config.username + ':' + infobip_config.password
            data_str = "%s:%s" % (infobip_config.username, infobip_config.password)
            data_bytes = data_str.encode("utf-8")
            base_64 = base64.b64encode(data_bytes)
            base_64 = str(base_64, 'utf-8')
            auth = "Basic %s" % (base_64)

            headers = {'authorization': auth, 'content-type': "application/json", 'accept': "application/json"}
            # _logger.info("\nHeader : %s",headers)
            conn.request("POST", "/sms/1/text/single", payload, headers)
            res = conn.getresponse()
            data = res.read()

            res = literal_eval(data.decode("utf-8"))
            print(res)

            #             send_sms_client = send_single_textual_sms(Configuration(infobip_config.username, infobip_config.password))
            #
            #             request = SMSTextualRequest()
            #             request.text = body_text or ''
            #             request.to = [send_to]
            #             response = send_sms_client.execute(request)
            #
            #             print(response)

            if keep_history:
                state = "draft"
                if "requestError" in res:
                    state = "fail"
                elif "messages" in res:
                    tmp_res = res.get("messages")[0]
                    if tmp_res and tmp_res["status"]["name"] == "MESSAGE_ACCEPTED":
                        state = "sent"
                    elif tmp_res and tmp_res["status"]["name"] == "PENDING_ENROUTE":
                        _logger.info("\n\nsent : %s", tmp_res["status"]["name"])
                        state = "sent"
                    elif tmp_res and tmp_res["status"]["name"] == "REJECTED_PREFIX_MISSING":
                        state = "reject"
                    elif tmp_res and tmp_res["status"]["name"] == "REJECTED_DESTINATION":
                        state = "reject"

                self.env['fl.infobip.sms.history'].create({"send_to": send_to, "send_body": body_text,
                                                           "state": state, "api_response": res})

        else:
            raise ValidationError(_(
                'Infobip SMS configuration missing. You can find inside Settings > Technical > Infobip SMS > Configuration'))

    @api.multi
    def send_sms_url(self, body_text=False, send_to=False, keep_history=True):
        # conn = http.client.HTTPSConnection("api.infobip.com")
        infobip_config = self.env['fl.infobip.sms'].search([], limit=1)
        if infobip_config and infobip_config.base_url and infobip_config.username and infobip_config.password:
            conn = client.HTTPSConnection(infobip_config.base_url)

            payload = "{\"messages\": [{\"from\": \"InfoSMS\",\"destinations\": [{\"to\": \"%s\"}],\"text\": \"%s\"}],\"tracking\": {\"track\": \"URL\",\"type\": \"SOCIAL_INVITES\"}}" % (send_to, body_text.encode('utf-8').decode('latin-1', 'ignore'))

            # "{\"from\":\"InfoSMS\",\"to\":\"%s\",\"text\":\"%s\"}" % (
            # send_to, body_text.encode('utf-8').decode('latin-1', 'ignore'))
            data_str = infobip_config.username + ':' + infobip_config.password
            data_str = "%s:%s" % (infobip_config.username, infobip_config.password)
            data_bytes = data_str.encode("utf-8")
            base_64 = base64.b64encode(data_bytes)
            base_64 = str(base_64, 'utf-8')
            auth = "Basic %s" % (base_64)

            headers = {'authorization': auth, 'content-type': "application/json", 'accept': "application/json"}
            # _logger.info("\nHeader : %s",headers)
            conn.request("POST", "/sms/1/text/advanced", payload, headers)
            res = conn.getresponse()
            data = res.read()

            res = literal_eval(data.decode("utf-8"))
            print(res)

            #             send_sms_client = send_single_textual_sms(Configuration(infobip_config.username, infobip_config.password))
            #
            #             request = SMSTextualRequest()
            #             request.text = body_text or ''
            #             request.to = [send_to]
            #             response = send_sms_client.execute(request)
            #
            #             print(response)

            if keep_history:
                state = "draft"
                if "requestError" in res:
                    state = "fail"
                elif "messages" in res:
                    tmp_res = res.get("messages")[0]
                    if tmp_res and tmp_res["status"]["name"] == "MESSAGE_ACCEPTED":
                        state = "sent"
                    elif tmp_res and tmp_res["status"]["name"] == "PENDING_ENROUTE":
                        _logger.info("\n\nsent : %s", tmp_res["status"]["name"])
                        state = "sent"
                    elif tmp_res and tmp_res["status"]["name"] == "REJECTED_PREFIX_MISSING":
                        state = "reject"
                    elif tmp_res and tmp_res["status"]["name"] == "REJECTED_DESTINATION":
                        state = "reject"

                self.env['fl.infobip.sms.history'].create({"send_to": send_to, "send_body": body_text,
                                                           "state": state, "api_response": res})

        else:
            raise ValidationError(_(
                'Infobip SMS configuration missing. You can find inside Settings > Technical > Infobip SMS > Configuration'))

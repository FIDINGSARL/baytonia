from odoo import models, fields, api
import requests
from datetime import datetime, date
import json
import logging

_logger = logging.getLogger("==== SMS Instance (FreshChat Message) ====")


class SmsInstance(models.Model):
    _inherit = "sms.instance"

    fc_token = fields.Text(string="Token")
    provider = fields.Selection(selection_add=[("freshchat_sms", "Freshchat Msg")])
    fc_namespace = fields.Char(string="Namespace", default="849427c2_06b9_4e02_af1b_e13161a75377")
    fc_url = fields.Char(string="URL")
    fc_number = fields.Char(string="From Number")
    template_ids = fields.One2many(comodel_name="freshchat.template", inverse_name="instance_id")

    @api.onchange("provider")
    def onchange_provider(self):
        if not self.name:
            if self.provider:
                if self.provider == "freshchat_sms":
                    self.name = "FreshChat SMS"
                else:
                    super(SmsInstance, self).onchange_provider()
            else:
                self.name = ""

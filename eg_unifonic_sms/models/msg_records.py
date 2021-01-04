from datetime import datetime, date, timedelta

from odoo import models, fields, api


class MsgRecords(models.Model):
    _name = "msg.records"

    to_number = fields.Char(string="To Number")
    message = fields.Text(string="Message")
    state = fields.Selection(
        [("draft", "Draft"), ("send", "Send"), ("failed", "Failed"), ("cancelled", "Cancelled"), ("error", "Error")],
        string="State")
    current_date = fields.Date(string="Create Date")

    @api.multi
    def send_msg_records(self):
        current_datetime = datetime.now()
        sms_instance_id = self.env["sms.instance"].search([("provider", "=", "unifonic_sms")])
        msg_record_ids = self.search([("state", "=", "draft")])
        for msg_record_id in msg_record_ids:
            try:
                self.env["post.sms.wizard"].send_sms(body=msg_record_id.message, dst_number=msg_record_id.to_number,
                                                     msg_record_id=msg_record_id)

            except Exception as e:
                msg_record_id.state = "error"
                self.env["msg.error.log"].create({"sms_instance_id": sms_instance_id.id,
                                                  "datetime": current_datetime,
                                                  "error_message": str(e),
                                                  "process": "Send SMS cron",
                                                  "order_detail": msg_record_id.message})

            self._cr.commit()

    @api.multi
    def send_failed_msg_records(self):
        msg_record_ids = self.search([("state", "=", "failed")])
        for msg_record_id in msg_record_ids:
            self.env["post.sms.wizard"].send_sms(body=msg_record_id.message, dst_number=msg_record_id.to_number,
                                                 msg_record_id=msg_record_id)

    @api.multi
    def change_state_msg_records(self):
        before_date = date.today() - timedelta(days=2)
        msg_record_ids = self.search([("state", "=", "failed"), ("current_date", "<=", str(before_date))])
        if msg_record_ids:
            msg_record_ids.write({"state": "cancelled"})

    @api.multi
    def send_msg_by_manual(self):
        msg_record_ids = self.browse(self._context.get("active_ids"))
        for msg_record_id in msg_record_ids:
            if msg_record_id.state in ["draft", "failed", "error"]:
                self.env["post.sms.wizard"].send_sms(body=msg_record_id.message, dst_number=msg_record_id.to_number,
                                                     msg_record_id=msg_record_id)

from odoo import models, fields, api
from datetime import datetime, date, timedelta
import logging

_logger = logging.getLogger("===Msg Delivery Report Get Status===")


class MsgDeliveryReport(models.Model):
    _name = "msg.delivery.report"
    _rec_name = "sms_instance_id"

    from_number = fields.Char(string="Form Number", readonly=True)
    to_number = fields.Char(string="To Number", readonly=True)
    body = fields.Text(string="Body", readonly=True)
    message_datetime = fields.Datetime(string="Message DateTime", default=datetime.now(), readonly=True)
    sid = fields.Char(string="SID", readonly=True)
    is_group = fields.Boolean(string="Is Group")
    is_parent = fields.Boolean(string="Is Parent")
    is_child = fields.Boolean(string="Is Child")
    message_title = fields.Char(string="Message Title")

    # Relation field
    sms_instance_id = fields.Many2one(comodel_name="sms.instance", string="Sms Instance", readonly=True)
    msg_status_id = fields.Many2one(comodel_name="msg.status", string="Status", readonly=True)
    is_last_status = fields.Boolean(related="msg_status_id.is_last_status", readonly=True, store=True)
    msg_delivery_report_id = fields.Many2one(comodel_name="msg.delivery.report", string="Msg Delivery Report")
    msg_delivery_report_ids = fields.One2many(comodel_name="msg.delivery.report", inverse_name="msg_delivery_report_id",
                                              string="Msg Delivery Reports")

    @api.multi
    def get_status_update(self):
        _logger.info("All Status are Update")

    @api.model
    def _get_status_update(self):
        current_datetime = datetime.now()
        yesterday_datetime = datetime.now() - timedelta(days=1)

        sms_instance_ids = self.env["sms.instance"].search([("active", "=", True)])

        msg_delivery_report_ids = self.search(
            [("msg_status_id.is_last_status", "=", False),
             ("sms_instance_id", "in", sms_instance_ids.ids), '&',
             ("message_datetime", "<=", str(current_datetime)),
             ("message_datetime", ">=", str(yesterday_datetime))])
        ctx = dict(self._context)
        ctx.update({'active_ids': msg_delivery_report_ids.ids})
        self.with_context(ctx).get_status_update()
        _logger.info("Successfully Cron Completed")

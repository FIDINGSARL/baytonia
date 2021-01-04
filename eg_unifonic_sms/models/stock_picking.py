from odoo import models, fields, api
import logging
from datetime import datetime, date

_logger = logging.getLogger("==== Delivery Order (Unifonic message) ====")


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def send_to_shipper(self):
        res = super(StockPicking, self).send_to_shipper()
        self._cr.commit()
        try:
            if self.carrier_tracking_ref:
                self.send_tracking_url_by_sms()
        except Exception as e:
            _logger.info(e)
            self.message_post(body='Error while sending tracking detail by sms')
        return res

    @api.multi
    def send_tracking_url_by_sms(self):
        current_date = date.today()
        current_datetime = datetime.now()
        url = self.carrier_id.tracking_url
        tracking_number = self.carrier_tracking_ref
        if url and tracking_number:
            tracking_url = "{}{}".format(url, tracking_number)
            instance_id = self.env["sms.instance"].search([("provider", "=", "unifonic_sms")])
            if instance_id:
                message = ""
                order_id = self.sale_id
                to_number = order_id.partner_id.phone
                if not to_number and order_id.partner_id.mobile:
                    to_number = order_id.partner_id.mobile
                elif not to_number and order_id.partner_invoice_id.phone:
                    to_number = order_id.partner_invoice_id.phone
                elif not to_number and order_id.partner_invoice_id.mobile:
                    to_number = order_id.partner_invoice_id.mobile
                if not to_number:
                    order_detail = "Order is {} and customer number is not available".format(order_id.name)
                    self.env["msg.error.log"].create({"sms_instance_id": instance_id.id,
                                                      "datetime": current_datetime,
                                                      "process": "Send SMS",
                                                      "order_detail": order_detail})
                    _logger.info("Customer number is not available for this order: {}".format(order_id.name))
                    return
                if instance_id.for_tracking_url:
                    message = instance_id.tracking_url_msg
                if message:
                    message = message.replace("{{order_number}}", order_id.name)
                    message = message.replace("{{total_amount}}", str(order_id.amount_total))
                    message = message.replace("{{state}}", order_id.state.capitalize())
                    message = message.replace("{{tracking_number}}", tracking_number)
                    message = message.replace("{{carrier_name}}", self.carrier_id and self.carrier_id.name or "")
                    message = message.replace("{{tracking_url}}", tracking_url)
                    message = message.replace("{{confirmation_date}}", order_id.confirmation_date or "")
                    message = message.replace("{{marketing_url}}", instance_id.marketing_url or "")
                    self.env["msg.records"].create({"to_number": to_number,
                                                    "message": message,
                                                    "state": "draft",
                                                    "current_date": current_date})

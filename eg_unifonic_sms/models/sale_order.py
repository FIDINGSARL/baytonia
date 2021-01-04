from odoo import models, fields, api
import logging
from datetime import datetime, date

_logger = logging.getLogger("==== Sale Order (Unifonic message) ====")


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def write(self, vals):
        current_date = date.today()
        current_datetime = datetime.now()
        res = super(SaleOrder, self).write(vals)
        state = vals.get("state")
        if state:
            instance_id = self.env["sms.instance"].search([("provider", "=", "unifonic_sms")])
            if instance_id:
                message = ""
                to_number = self.partner_id.phone
                if not to_number and self.partner_id.mobile:
                    to_number = self.partner_id.mobile
                elif not to_number and self.partner_invoice_id.phone:
                    to_number = self.partner_invoice_id.phone
                elif not to_number and self.partner_invoice_id.mobile:
                    to_number = self.partner_invoice_id.mobile
                if not to_number:
                    _logger.info("Customer number is not available for this order: {}".format(self.name))
                    order_detail = "Order is {} and customer number is not available".format(self.name)
                    self.env["msg.error.log"].create({"sms_instance_id": instance_id.id,
                                                      "datetime": current_datetime,
                                                      "process": "Send SMS",
                                                      "order_detail": order_detail})
                else:
                    tracking_number = ""
                    tracking_url = ""
                    if state == "sent":
                        if instance_id.for_sent:
                            message = instance_id.sent_msg

                    elif state == "sale":
                        if instance_id.for_sale:
                            message = instance_id.sale_msg

                    elif state == "done":
                        if instance_id.for_done:
                            message = instance_id.done_msg

                    elif state == "cancel":
                        if instance_id.for_cancel:
                            message = instance_id.cancel_msg
                    for picking_id in self.picking_ids:
                        if picking_id.state == "done":
                            tracking_number = picking_id.carrier_tracking_ref
                            tracking_url = "{}{}".format(picking_id.carrier_id.tracking_url,
                                                         picking_id.carrier_tracking_ref)
                            break
                    if message:
                        message = message.replace("{{order_number}}", self.name)
                        message = message.replace("{{total_amount}}", str(self.amount_total))
                        message = message.replace("{{state}}", self.state.capitalize())
                        message = message.replace("{{tracking_number}}", tracking_number or "")
                        message = message.replace("{{carrier_name}}", self.carrier_id and self.carrier_id.name or "")
                        message = message.replace("{{tracking_url}}", tracking_url or "")
                        message = message.replace("{{confirmation_date}}", self.confirmation_date or "")
                        message = message.replace("{{marketing_url}}", instance_id.marketing_url or "")
                        self.env["msg.records"].create({"to_number": to_number,
                                                        "message": message,
                                                        "state": "draft",
                                                        "current_date": current_date})

        return res

    @api.multi
    def send_msg_for_draft(self):
        current_date = date.today()
        current_datetime = datetime.now()
        state = self.state
        if state:
            instance_id = self.env["sms.instance"].search([("provider", "=", "unifonic_sms")])
            if instance_id:
                message = ""
                to_number = self.partner_id.phone
                if not to_number and self.partner_id.mobile:
                    to_number = self.partner_id.mobile
                elif not to_number and self.partner_invoice_id.phone:
                    to_number = self.partner_invoice_id.phone
                elif not to_number and self.partner_invoice_id.mobile:
                    to_number = self.partner_invoice_id.mobile
                if not to_number:
                    _logger.info("Customer number is not available for this order: {}".format(self.name))
                    order_detail = "Order is {} and customer number is not available".format(self.name)
                    self.env["msg.error.log"].create({"sms_instance_id": instance_id.id,
                                                      "datetime": current_datetime,
                                                      "process": "Send SMS",
                                                      "order_detail": order_detail})
                else:
                    if state == "draft":
                        if instance_id.for_draft:
                            message = instance_id.draft_msg
                    if message:
                        message = message.replace("{{order_number}}", self.name)
                        message = message.replace("{{total_amount}}", str(self.amount_total))
                        message = message.replace("{{state}}", self.state.capitalize())
                        message = message.replace("{{confirmation_date}}", self.confirmation_date or "")
                        message = message.replace("{{marketing_url}}", instance_id.marketing_url or "")
                        self.env["msg.records"].create({"to_number": to_number,
                                                        "message": message,
                                                        "state": "draft",
                                                        "current_date": current_date})

from datetime import date
from odoo import models, api, fields
from datetime import date, timedelta, datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class DeliveryTrackingLine(models.Model):
    _inherit = "delivery.tracking.line"

    is_send = fields.Boolean("Message Send")

    def send_sms_review(self):
        current_date = date.today()
        back_date = datetime.today() - timedelta(days=7)
        back_date_str = back_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        clex_tracking_line_ids = self.search(['|', ('status_id.name', 'ilike', 'Shipment Delivered to'),
                                              ('status_id.name', 'ilike', 'Shipment Money Collected (COD)'),
                                              ('create_date', '>=', back_date_str)])

        for tracking_line in clex_tracking_line_ids:

            if not tracking_line.is_send:

                name = tracking_line.picking_id.partner_id.name
                if tracking_line.picking_id.sale_id:
                    refrence = tracking_line.picking_id.sale_id.name
                else:
                    refrence = tracking_line.tracking_ref
                to_number = tracking_line.picking_id.partner_id.phone
                content = 'أهلا %s وصلك طلبك رقم  %s وحابين نسمع رأيك عن تجربتك مع بيتونيا من خلال الرابط التالي: https://oddo.baytonia.com/survey/start/1?order=%s' % (
                    refrence, name, refrence)
                if to_number:
                    msg_records = self.env["msg.records"].create({"to_number": to_number,
                                                                  "message": content,
                                                                  "state": "draft",
                                                                  "current_date": current_date})
                    msg_records.send_msg_records()
                    tracking_line.is_send = True

        aramex_tracking_line_ids = self.search(
            ['|', ('status_id.name', 'ilike', 'Delivered'), ('status_id.name', 'ilike', 'Collected by Consignee'),
             ('create_date', '>=', back_date_str)])
        for tracking_line in aramex_tracking_line_ids:

            if not tracking_line.is_send:

                name = tracking_line.picking_id.partner_id.name
                if tracking_line.picking_id.sale_id:
                    refrence = tracking_line.picking_id.sale_id.name
                else:
                    refrence = tracking_line.tracking_ref
                to_number = tracking_line.picking_id.partner_id.phone
                content = 'أهلا %s وصلك طلبك رقم  %s وحابين نسمع رأيك عن تجربتك مع بيتونيا من خلال الرابط التالي: https://oddo.baytonia.com/survey/start/1?order=%s' % (
                    refrence, name, refrence)
                if to_number:
                    msg_records = self.env["msg.records"].create({"to_number": to_number,
                                                                  "message": content,
                                                                  "state": "draft",
                                                                  "current_date": current_date})
                    msg_records.send_msg_records()
                    tracking_line.is_send = True

        smsa_tracking_line_ids = self.search(
            ['|', ('status_id.name', 'ilike', 'Shipment Delivered'),
             ('status_id.name', 'ilike', 'PROOF OF DELIVERY CAPTURED'),
             ('create_date', '>=', back_date_str)])
        for tracking_line in smsa_tracking_line_ids:
            if not tracking_line.is_send:

                name = tracking_line.picking_id.partner_id.name
                if tracking_line.picking_id.sale_id:
                    refrence = tracking_line.picking_id.sale_id.name
                else:
                    refrence = tracking_line.tracking_ref
                to_number = tracking_line.picking_id.partner_id.phone
                content = 'أهلا %s وصلك طلبك رقم  %s وحابين نسمع رأيك عن تجربتك مع بيتونيا من خلال الرابط التالي: https://oddo.baytonia.com/survey/start/1?order=%s' % (
                    refrence, name, refrence)
                if to_number:
                    msg_records = self.env["msg.records"].create({"to_number": to_number,
                                                                  "message": content,
                                                                  "state": "draft",
                                                                  "current_date": current_date})
                    msg_records.send_msg_records()
                    tracking_line.is_send = True

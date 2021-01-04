from odoo import models, fields, api
from datetime import datetime, date, timedelta


class DeliveryTrackingLine(models.Model):
    _inherit = "delivery.tracking.line"

    @api.model
    def create(self, vals):
        res = super(DeliveryTrackingLine, self).create(vals)
        if res.picking_id:
            instance_id = self.env["sms.instance"].search([("provider", "=", "unifonic_sms")], limit=1)
            if instance_id:
                message = instance_id.tracking_line_msg
                current_date = date.today()
                to_number = res.picking_id.partner_id.phone or res.picking_id.partner_id.mobile or ""
                if to_number:
                    self.env["msg.records"].create({"to_number": to_number,
                                                    "message": message,
                                                    "state": "draft",
                                                    "current_date": current_date})
        return res

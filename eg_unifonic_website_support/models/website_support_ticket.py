from odoo import models, fields, api
import logging

_logger = logging.getLogger("=== Website Support Ticket ===")


class WebsiteSupportTicket(models.Model):
    _inherit = "website.support.ticket"

    @api.multi
    def write(self, vals):
        res = super(WebsiteSupportTicket, self).write(vals)
        for rec in self:
            if vals.get("user_id"):
                dst_number = None
                partner_id = None
                if rec.partner_id:
                    dst_number = rec.partner_id.phone or rec.partner_id.mobile or None
                    partner_id = rec.partner_id
                if rec.sale_order_id and not dst_number:
                    dst_number = rec.sale_order_id.partner_id.phone or rec.sale_order_id.partner_id.mobile or None
                    partner_id = rec.sale_order_id.partner_id
                    if not dst_number:
                        dst_number = rec.sale_order_id.partner_shipping_id.phone or rec.sale_order_id.partner_shipping_id.mobile or None
                        partner_id = rec.sale_order_id.partner_shipping_id

                if rec.stock_picking_id and not dst_number:
                    dst_number = rec.stock_picking_id.partner_id.phone or rec.stock_picking_id.partner_id.mobile or None
                    partner_id = rec.stock_picking_id.partner_id

                instance_id = self.env["sms.instance"].search([("provider", "=", "unifonic_sms")])
                body = instance_id and instance_id.user_assign_msg or ""
                body = body.replace("{{person_name}}", partner_id and partner_id.name or "")
                body = body.replace("{{ticket_number}}", rec.ticket_number)
                if body and dst_number:
                    self.env["post.sms.wizard"].send_sms(body=body, dst_number=dst_number)
                else:
                    _logger.info("Partner number not found!!!")
        return res

from odoo import models, fields, api
from odoo.exceptions import Warning


class MsgByUnifonic(models.TransientModel):
    _name = "msg.by.unifonic"

    number = fields.Char(string="Number")
    message = fields.Text(string="Message")

    @api.model
    def default_get(self, fields_list):
        res = super(MsgByUnifonic, self).default_get(fields_list)
        picking_id = self.env["stock.picking"].browse(self._context.get("active_id"))
        sms_instance_id = self.env["sms.instance"].search([("provider", "=", "unifonic_sms")], limit=1)
        if picking_id and sms_instance_id:
            message = sms_instance_id.return_disclaimer_msg
            dst_number = picking_id.partner_id.phone or picking_id.partner_id.mobile or None
            if message:
                url = "https://oddo.baytonia.com/delivery_return/confirm/{}".format(picking_id.id)
                message = message.replace("{{order_number}}", picking_id.name)
                message = message.replace("{{customer_name}}", picking_id.partner_id.name)
                message = message.replace("{{total_amount}}", str(picking_id.total_amount))
                message = message.replace("{{return_approve_url}}", url)
            res["number"] = dst_number
            res["message"] = message
        return res

    @api.multi
    def send_msg_customer_by_unifonic(self):
        if self.message and self.number:
            self.env["post.sms.wizard"].send_sms(body=self.message, dst_number=self.number)
        else:
            raise Warning("Number and Message are required")

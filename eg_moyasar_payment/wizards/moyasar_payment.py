from odoo import models, fields, api
import moyasar
from odoo.exceptions import Warning


class MoyasarPayment(models.TransientModel):
    _name = "moyasar.payment"

    total_amount = fields.Float(string="Total Amount")
    message = fields.Char(string="Message")
    moyasar_config_id = fields.Many2one(comodel_name="moyasar.configuration", string="Configuration")
    partner_id = fields.Many2one(comodel_name="res.partner", string="Customer")
    phone = fields.Char(string="Phone")
    sale_partner_id = fields.Many2one(comodel_name="res.partner", string="Customer")

    @api.model
    def default_get(self, fields_list):
        res = super(MoyasarPayment, self).default_get(fields_list)
        order_id = self.env["sale.order"].browse(self._context.get("active_id"))
        sms_instance_id = self.env["sms.instance"].search([("provider", "=", "unifonic_sms")])
        if order_id and sms_instance_id:
            message = sms_instance_id.moyasar_message
            if message:
                # message = message.replace("{{invoice_number}}", order_id.name)
                message = message.replace("{{order_number}}", order_id.name)
            if "total_amount" in fields_list:
                res["total_amount"] = order_id.amount_total
                res["message"] = message
                res["sale_partner_id"] = order_id.partner_id.id
        return res

    @api.onchange("partner_id")
    def onchange_on_partner(self):
        if self.partner_id:
            self.phone = self.partner_id.phone or self.partner_id.mobile
        else:
            self.phone = ""

    @api.multi
    def generate_and_send_payment_url(self):
        # if not self.message or not self.total_amount or not self.moyasar_config_id:
        #     raise Warning("Message, Total amount and configuration are required!!!")
        order_id = self.env["sale.order"].browse(self._context.get("active_id"))
        if order_id:
            # to_number = order_id.partner_id.phone or order_id.partner_id.mobile
            # if not to_number:
            #     raise Warning("Please add number of customer")
            moyasar_id = self.moyasar_config_id
            data = {"amount": int(self.total_amount * 100), "currency": moyasar_id.currency,
                    "description": order_id.name, "callback_url": moyasar_id.callback_url or ""}
            moyasar.api_key = moyasar_id.live_sk if moyasar_id.prod_environment else moyasar_id.test_sk
            try:
                response = moyasar.Invoice.create(data)
            except Exception as e:
                raise Warning("{}".format(e))
            if response.status == "initiated":
                invoice_url = response.url
                order_id.write({"moyasar_payment_id": response.id})
                body = self.message.replace("{{moyasar_url}}", invoice_url)
                to_number = self.phone
                if self._context.get('copy') == "yes":
                    raise Warning(body)
                if self._context.get('whatsapp') == "yes":
                    url = 'https://web.whatsapp.com/send?phone='
                    if to_number:
                        dst_number = to_number
                        dst_number = dst_number.lstrip("0")
                        dst_number = dst_number.lstrip("+")
                        dst_number = dst_number.lstrip("966")
                        to_number = "+966{}".format(dst_number)
                    url += to_number + "&text=" + body
                    return {'type': 'ir.actions.act_url',
                            'name': "Send Sale Payment URL",
                            'target': 'new',
                            'url': url}
                response_message = self.env["post.sms.wizard"].send_sms(self, body=body, dst_number=to_number)
                if response_message and response_message != "Success":
                    raise Warning("Send Message : {} \n URL : {}".format(response_message, invoice_url))
                action = self.env.ref("eg_moyasar_payment.action_moyasar_payment_new").read()[0]
                action['views'] = [(self.env.ref('eg_moyasar_payment.moyasar_payment_new_form_view').id, 'form')]
                action['res_id'] = self.id
                return action
            else:
                raise Warning("{}".format(response.__dict__))

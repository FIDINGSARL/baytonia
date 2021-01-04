from odoo import models, fields, api


class WhatsappMessageWizard(models.TransientModel):
    _name = "whatsapp.message.wizard"

    to_number = fields.Char("To Number")
    msg = fields.Text("Message")
    picking_ids = fields.Many2many("stock.picking")
    picking_id = fields.Many2one("stock.picking")
    message_type = fields.Selection([("tracking", "Tracking"), ("bank_details", "Bank Details")])

    @api.model
    def default_get(self, fields_list):
        res = super(WhatsappMessageWizard, self).default_get(fields_list)
        order_id = self.env["sale.order"].browse(self._context.get('active_id'))
        if 'picking_ids' in fields_list:
            res.update({'picking_ids': [(6, 0, order_id.picking_ids.ids)]})

        if "to_number" in fields_list:
            to_number = order_id.partner_id.phone
            if not to_number and order_id.partner_id.mobile:
                to_number = order_id.partner_id.mobile
            elif not to_number and order_id.partner_invoice_id.phone:
                to_number = order_id.partner_invoice_id.phone
            elif not to_number and order_id.partner_invoice_id.mobile:
                to_number = order_id.partner_invoice_id.mobile
            if to_number:
                dst_number = to_number
                dst_number = dst_number.lstrip("0")
                dst_number = dst_number.lstrip("+")
                dst_number = dst_number.lstrip("966")
                dst_number = "+966{}".format(dst_number)
                res.update({"to_number": dst_number})
        return res

    @api.onchange('picking_id')
    def _onchange_picking_id(self):
        if self.picking_id:
            url = self.picking_id.carrier_id.tracking_url
            tracking_number = self.picking_id.carrier_tracking_ref
            if url and tracking_number:
                tracking_url = "{}{}".format(url, tracking_number)
                self.msg = tracking_url

    @api.onchange("message_type")
    def _onchange_message_type(self):
        self.picking_id = False
        order_id = self.env["sale.order"].browse(self._context.get('active_id'))
        if self.message_type == "bank_details":
            self.msg = """عميلنا العزيز تم استلام طلبك رقم {} 

الرجاء تحويل المبلغ خلال ال ٢٤ ساعه القادمة لحجز منتجاتكم و تأكيد الطلب 

مؤسسه قطنه المنزل 
البنك الأهلي التجاري 
14581274000108
آيبان 
SA6710000014581274000108
بنك الراجحي :
161608010304603
آيبان
SA8880000161608010304603

وارسال صوره من إيصال التحويل البنكي عالرقم 00966920022468 عن طريق الواتس""".format(order_id.name,
                                                                                   order_id.amount_total)
        elif self.message_type == "tracking":
            self.msg = ""

    @api.multi
    def send_whatsapp_message(self):
        url = 'https://web.whatsapp.com/send?phone='
        url += self.to_number + "&text=" + self.msg
        return {'type': 'ir.actions.act_url',
                'name': "Send Sale Order",
                'target': 'new',
                'url': url}

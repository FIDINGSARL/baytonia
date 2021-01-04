from odoo import models, fields, api
from datetime import timedelta, date, datetime


class SaleOrderSms(models.TransientModel):
    _name = "sale.order.sms"

    text = fields.Text("Message")
    message_medium = fields.Selection([('sms', 'SMS'), ('email', 'EMAIL'), ('both', 'BOTH')], default='both',
                                      string="SMS/EMAIL", required=True)

    @api.multi
    def send_sms(self):

        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids'))

        # msg send function
        if self.message_medium == 'sms':
            for sale_order in sale_orders:
                content = self.text.replace('$name$', sale_order.partner_id.name).replace('$order_number$',
                                                                                          sale_order.name)
                current_date = date.today()
                to_number = sale_order.partner_invoice_id.phone
                if to_number:
                    msg_records = self.env["msg.records"].create({"to_number": to_number,
                                                                  "message": content,
                                                                  "state": "draft",
                                                                  "current_date": current_date})

                    msg_records.send_msg_records()
        if self.message_medium == 'email':
            for sale_order in sale_orders:
                content = self.text.replace('$name$', sale_order.partner_id.name).replace('$order_number$',
                                                                                          sale_order.name)
                sale_order.update({'msg_body': content})
                ir_model_data = self.env['ir.model.data']

                try:
                    template_id = \
                        ir_model_data.get_object_reference('odx_auto_sms_email', 'email_template_edi_sale_new')[
                            1]
                except ValueError:
                    template_id = False
                ctx = {
                    'default_model': 'sale.order',
                    'default_res_id': sale_order.id,
                    'default_use_template': True,
                    'default_template_id': self.env.ref('odx_auto_sms_email.email_template_edi_sale_new'),
                    'default_composition_mode': 'comment',
                    'web_base_url': self.env['ir.config_parameter'].get_param('web.base.url'),
                    'mark_so_as_sent': True,
                    'body_msg': content,
                    'custom_layout': "sale.mail_template_data_notification_email_sale_order",
                    'proforma': self.env.context.get('proforma', False),
                    'force_email': True
                }
                template = self.env['mail.template'].browse(template_id)
                html_body = template.body_html
                text = template.with_context(ctx).render_template(html_body, 'sale.order',
                                                                  sale_order.id)
                # for email_recipients in email_to:
                compose = self.env['mail.mail'].with_context(ctx).create({
                    'subject': 'Sale order',
                    'body_html': text,
                    'email_to': sale_order.partner_id.email,
                })
                compose.send()

        if self.message_medium == 'both':
            for sale_order in sale_orders:
                content = self.text.replace('$name$', sale_order.partner_id.name).replace('$order_number$',
                                                                                          sale_order.name)
                current_date = date.today()
                to_number = sale_order.partner_invoice_id.phone
                if to_number:
                    msg_records = self.env["msg.records"].create({"to_number": to_number,
                                                                  "message": content,
                                                                  "state": "draft",
                                                                  "current_date": current_date})

                    msg_records.send_msg_records()
                sale_order.update({'msg_body': content})
                ir_model_data = self.env['ir.model.data']

                try:
                    template_id = \
                        ir_model_data.get_object_reference('odx_auto_sms_email', 'email_template_edi_sale_new')[
                            1]
                except ValueError:
                    template_id = False
                ctx = {
                    'default_model': 'sale.order',
                    'default_res_id': sale_order.id,
                    'default_use_template': True,
                    'default_template_id': self.env.ref('odx_auto_sms_email.email_template_edi_sale_new'),
                    'default_composition_mode': 'comment',
                    'web_base_url': self.env['ir.config_parameter'].get_param('web.base.url'),
                    'mark_so_as_sent': True,
                    'body_msg': content,
                    'custom_layout': "sale.mail_template_data_notification_email_sale_order",
                    'proforma': self.env.context.get('proforma', False),
                    'force_email': True
                }
                template = self.env['mail.template'].browse(template_id)
                html_body = template.body_html
                text = template.with_context(ctx).render_template(html_body, 'sale.order',
                                                                  sale_order.id)
                # for email_recipients in email_to:
                compose = self.env['mail.mail'].with_context(ctx).create({
                    'subject': 'Sale order',
                    'body_html': text,
                    'email_to': sale_order.partner_id.email,
                })
                compose.send()

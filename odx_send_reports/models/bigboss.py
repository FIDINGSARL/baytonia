from odoo import models, fields, api
import base64
from datetime import date, timedelta, datetime



class ToolboxDashboard(models.Model):
    _inherit = 'toolbox.dashboard'

    def send_reports(self):

        from_date = str(date.today() - timedelta(days=7))
        to_date = str(date.today())

        pdf = self.env.ref('odx_send_reports.orderd_qty_action').render_qweb_pdf(self.ids)
        b64_pdf = base64.b64encode(pdf[0])

        ATTACHMENT_NAME = "Product % Sale Report Ordered Qty"
        attachment_id = self.env['ir.attachment'].create({
            'name': ATTACHMENT_NAME,
            'type': 'binary',
            'datas': b64_pdf,
            'datas_fname': ATTACHMENT_NAME + '.pdf',
            'store_fname': ATTACHMENT_NAME,
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/x-pdf'
        })

        ir_model_data = self.env['ir.model.data']

        try:
            template_id = \
                ir_model_data.get_object_reference('odx_send_reports', 'email_template_orderd_qty')[
                    1]
        except ValueError:
            template_id = False
        ctx = {
            'default_model': None,
            'default_res_id': None,
            'default_use_template': True,
            'default_template_id': self.env.ref('odx_send_reports.email_template_orderd_qty'),
            'default_composition_mode': 'comment',
            'web_base_url': self.env['ir.config_parameter'].get_param('web.base.url'),
            'mark_so_as_sent': True,
            'custom_layout': "sale.mail_template_data_notification_email_sale_order",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True
        }
        template = self.env['mail.template'].browse(template_id)
        html_body = template.body_html
        # for email_recipients in email_to:
        compose = self.env['mail.mail'].with_context(ctx).create({
            'subject':  'Product % Sale Report Ordered Qty : ' + from_date+ ' ' +' To ' + ' ' + to_date,
            'body_html': html_body,
            'email_to': template.email_to,
            'email_cc': template.email_to,
            'attachment_ids': [(6, 0, [attachment_id.id])] or None,

        })
        compose.send()



        pdf = self.env.ref('odx_send_reports.product_percent_invoiced_qty_action').render_qweb_pdf(self.ids)
        b64_pdf = base64.b64encode(pdf[0])

        ATTACHMENT_NAME = "Product % Sale Report Invoiced Qty"
        attachment_id = self.env['ir.attachment'].create({
            'name': ATTACHMENT_NAME,
            'type': 'binary',
            'datas': b64_pdf,
            'datas_fname': ATTACHMENT_NAME + '.pdf',
            'store_fname': ATTACHMENT_NAME,
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/x-pdf'
        })


        compose = self.env['mail.mail'].with_context(ctx).create({
            'subject': 'Product % Sale Report Invoiced Qty : ' + from_date + ' ' + ' To ' + ' ' + to_date,
            'body_html': html_body,
            'email_to': template.email_to,
            'email_cc': template.email_to,
            'attachment_ids': [(6, 0, [attachment_id.id])] or None,

        })
        compose.send()

        pdf = self.env.ref('odx_send_reports.product_percent_delivered_qty_action').render_qweb_pdf(self.ids)
        b64_pdf = base64.b64encode(pdf[0])

        ATTACHMENT_NAME = "Product % Sale Report Delivered Qty"
        attachment_id = self.env['ir.attachment'].create({
            'name': ATTACHMENT_NAME,
            'type': 'binary',
            'datas': b64_pdf,
            'datas_fname': ATTACHMENT_NAME + '.pdf',
            'store_fname': ATTACHMENT_NAME,
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/x-pdf'
        })

        compose = self.env['mail.mail'].with_context(ctx).create({
            'subject': 'Product % Sale Report Delivered Qty : ' + from_date + ' ' + ' To ' + ' ' + to_date,
            'body_html': html_body,
            'email_to': template.email_to,
            'email_cc': template.email_to,
            'attachment_ids': [(6, 0, [attachment_id.id])] or None,

        })
        compose.send()

        pdf = self.env.ref('odx_send_reports.list_of_stock_product_action').render_qweb_pdf(self.ids)
        b64_pdf = base64.b64encode(pdf[0])

        ATTACHMENT_NAME = "List Of Stock Product"
        attachment_id = self.env['ir.attachment'].create({
            'name': ATTACHMENT_NAME,
            'type': 'binary',
            'datas': b64_pdf,
            'datas_fname': ATTACHMENT_NAME + '.pdf',
            'store_fname': ATTACHMENT_NAME,
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/x-pdf'
        })

        try:
            template_id = \
                ir_model_data.get_object_reference('odx_send_reports', 'email_template_stock_product')[
                    1]
        except ValueError:
            template_id = False
        ctx = {
            'default_model': None,
            'default_res_id': None,
            'default_use_template': True,
            'default_template_id': self.env.ref('odx_send_reports.email_template_stock_product'),
            'default_composition_mode': 'comment',
            'web_base_url': self.env['ir.config_parameter'].get_param('web.base.url'),
            'mark_so_as_sent': True,
            'custom_layout': "sale.mail_template_data_notification_email_sale_order",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True
        }
        template = self.env['mail.template'].browse(template_id)
        html_body = template.body_html
        # for email_recipients in email_to:
        compose = self.env['mail.mail'].with_context(ctx).create({
            'subject': 'List Of Stock Product : ' + from_date + ' ' + ' To ' + ' ' + to_date,
            'body_html': html_body,
            'email_to': template.email_to,
            'email_cc': template.email_to,
            'attachment_ids': [(6, 0, [attachment_id.id])] or None,

        })
        compose.send()

        pdf = self.env.ref('odx_send_reports.list_of_mto_product_action').render_qweb_pdf(self.ids)
        b64_pdf = base64.b64encode(pdf[0])

        ATTACHMENT_NAME = "List Of Mto Product"
        attachment_id = self.env['ir.attachment'].create({
            'name': ATTACHMENT_NAME,
            'type': 'binary',
            'datas': b64_pdf,
            'datas_fname': ATTACHMENT_NAME + '.pdf',
            'store_fname': ATTACHMENT_NAME,
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/x-pdf'
        })

        try:
            template_id = \
                ir_model_data.get_object_reference('odx_send_reports', 'email_template_mto_product')[
                    1]
        except ValueError:
            template_id = False
        ctx = {
            'default_model': None,
            'default_res_id': None,
            'default_use_template': True,
            'default_template_id': self.env.ref('odx_send_reports.email_template_mto_product'),
            'default_composition_mode': 'comment',
            'web_base_url': self.env['ir.config_parameter'].get_param('web.base.url'),
            'mark_so_as_sent': True,
            'custom_layout': "sale.mail_template_data_notification_email_sale_order",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True
        }
        template = self.env['mail.template'].browse(template_id)
        html_body = template.body_html
        # for email_recipients in email_to:
        compose = self.env['mail.mail'].with_context(ctx).create({
            'subject': 'List Of Mto Product : ' + from_date + ' ' + ' To ' + ' ' + to_date,
            'body_html': html_body,
            'email_to': template.email_to,
            'email_cc': template.email_to,
            'attachment_ids': [(6, 0, [attachment_id.id])] or None,

        })
        compose.send()

        pdf = self.env.ref('odx_send_reports.non_moving_product_action').render_qweb_pdf(self.ids)
        b64_pdf = base64.b64encode(pdf[0])

        ATTACHMENT_NAME = "Non Moving Product"
        attachment_id = self.env['ir.attachment'].create({
            'name': ATTACHMENT_NAME,
            'type': 'binary',
            'datas': b64_pdf,
            'datas_fname': ATTACHMENT_NAME + '.pdf',
            'store_fname': ATTACHMENT_NAME,
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/x-pdf'
        })

        try:
            template_id = \
                ir_model_data.get_object_reference('odx_send_reports', 'email_template_non_moving_product')[
                    1]
        except ValueError:
            template_id = False
        ctx = {
            'default_model': None,
            'default_res_id': None,
            'default_use_template': True,
            'default_template_id': self.env.ref('odx_send_reports.email_template_non_moving_product'),
            'default_composition_mode': 'comment',
            'web_base_url': self.env['ir.config_parameter'].get_param('web.base.url'),
            'mark_so_as_sent': True,
            'custom_layout': "sale.mail_template_data_notification_email_sale_order",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True
        }
        template = self.env['mail.template'].browse(template_id)
        html_body = template.body_html
        # for email_recipients in email_to:
        compose = self.env['mail.mail'].with_context(ctx).create({
            'subject': 'Non Moving Product : ' + from_date + ' ' + ' To ' + ' ' + to_date,
            'body_html': html_body,
            'email_to': template.email_to,
            'email_cc': template.email_to,
            'attachment_ids': [(6, 0, [attachment_id.id])] or None,

        })
        compose.send()


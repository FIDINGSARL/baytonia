from odoo import api, fields, models
from datetime import datetime,date,timedelta,time
import base64

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    @api.model
    def print_report(self,use_new_cursor=False, company_id=False):

            Mail = self.env['mail.mail']
            REPORT_ID = 'sale_report_daily.report_actions'
            pdf = self.env.ref(REPORT_ID).render_qweb_pdf(self.ids,{'dat':'daily'})
            b64_pdf = base64.b64encode(pdf[0])
            ATTACHMENT_NAME = "My Attachment Name"
            attachment_id= self.env['ir.attachment'].create({
                'name': ATTACHMENT_NAME,
                'type': 'binary',
                'datas': b64_pdf,
                'datas_fname': ATTACHMENT_NAME + '.pdf',
                'store_fname': ATTACHMENT_NAME,
                'res_model': self._name,
                'res_id': self.id,
                'mimetype': 'application/x-pdf'
            })
            email_template = self.env['ir.model.data'].get_object('sale_report_daily', 'email_template_daily_sale')

            values = {
                'model': None,
                'res_id': None,
                'subject': email_template.subject,
                'body': '',
                'body_html': email_template.body_html,
                'parent_id': None,
                'attachment_ids': [(6, 0, [attachment_id.id])] or None,
                'email_from': email_template.email_from,
                # 'auto_delete': True,
                'email_to':email_template.email_to,
                'email_cc':email_template.email_cc
            }
            print( values)
            Mail.create(values).send()
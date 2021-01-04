import base64
import logging

import requests

from odoo import models
from odoo.exceptions import Warning, ValidationError

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def clex_delivery_return_send_shipping(self):
        clex_id = self.env['delivery.carrier'].search([('delivery_type', '=', 'clex_delivery')])
        if clex_id:
            clex_id.clex_delivery_return_send_shipping(self)
        else:
            raise ValidationError("Clex not found")

    def clex_delivery_send_return_label_to_customer(self):
        if self.partner_id.email:
            attachment_id = self.env['ir.attachment']
            url = "http://cockpit.clexsa.com/pdf/download/%s?id=%s&type=A4-consignment_clex_label&return_type=pdf" % (
                self.return_tracking_ref, self.return_tracking_ref)
            headers = {"Content-Type": "application/json",
                       "Access-token": self.return_carrier_id.clex_access_token}
            try:
                response_body = requests.request("POST", url, headers=headers)
                if response_body.status_code == 200:
                    results = response_body.json()
                    _logger.info(["CLEX Delivery label Generation Response Data %s" % results])
                    label_url = results.get('data').get('awb_pdf_url')
                    if label_url:
                        label = base64.b64encode(requests.get(label_url).content)
                        attachment_id = self.env['ir.attachment'].create({
                            'datas': label,
                            'name': 'return_lable_{}.pdf'.format(self.return_tracking_ref),
                            'datas_fname': 'return_lable_{}.pdf'.format(self.return_tracking_ref)})

                    else:
                        raise Warning("%s" % response_body.text)

                else:
                    raise Warning("%s" % response_body.text)

            except Exception as e:
                raise Warning(e)
            msg = "اهلين {}        مرفق بوليصة الشحن للاسترجع            فريق بيتونيا                  baytonia.com".format(
                self.partner_id.name)
            values = {
                'model': 'sale.order',
                'res_id': self.id,
                'subject': "Return shipment label",
                'body': "",
                'body_html': msg,
                'parent_id': None,
                'attachment_ids': [(6, 0, attachment_id.ids)] or None,
                'email_from': "wecare@baytonia.com",
                'email_to': self.partner_id.email,
            }
            mail_id = self.env['mail.mail']
            mail_id.create(values).send()

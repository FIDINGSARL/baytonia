import json
import logging

import requests

from odoo import models, fields, api
from odoo.exceptions import Warning

_logger = logging.getLogger("======Export Tracking=====")


class StockPicking(models.Model):
    _inherit = "stock.picking"

    eg_magento_payment_method_id = fields.Many2one("magento.payment.method", "M Payment Method")

    @api.model
    def create(self, vals):
        """
        To assign magento payment method to backorder
        :param vals:
        :return:
        """
        res = super(StockPicking, self).create(vals)
        if res.backorder_id and res.backorder_id.eg_magento_payment_method_id:
            res.eg_magento_payment_method_id = res.backorder_id.eg_magento_payment_method_id.id
        return res

    @api.multi
    def send_to_shipper(self):
        res = super(StockPicking, self).send_to_shipper()
        self._cr.commit()
        try:
            if self.carrier_tracking_ref:
                self.action_sync_tracking_no()
                self.send_tracking_to_magento()
        except Exception as e:
            _logger.info(e)
            self.message_post(body='Error while exporting tracking number to magento, Kindly process manually')
        try:
            if self.carrier_tracking_ref and self.sale_id:
                self.send_tracking_email()
        except Exception as e:
            _logger.info(e)
            self.message_post(body='Error while sending email of tracking number to the customer')
        return res

    def send_tracking_email(self):
        if self.sale_id:
            subject = "Baytonia || {} Order shipped".format(self.sale_id.name)
            body_html = "<p>Hello {}</p></b> Your order {} has been shiped with {} carrier and tracking number {}." \
                        " You can track your parcel by clicking <a href='{}'>Track Now</a>.</b>" \
                        "<p>Thanks</p>".format(
                self.sale_id.partner_id.name, self.sale_id.name, self.carrier_id.name, self.carrier_tracking_ref,
                self.sale_id.carrier_details)
            values = {
                'model': None,
                'res_id': None,
                'subject': subject,
                'body': '',
                'body_html': body_html,
                'parent_id': None,
                'email_from': "wecare@baytonia.com",
                'email_to': self.sale_id.partner_id.email,
            }
            mail_id = self.env['mail.mail']
            mail_id.create(values).send()

    def send_tracking_to_magento(self):
        for picking_id in self:
            ctx = dict(self._context)
            text = ""
            status = "no"
            if picking_id.carrier_tracking_url and picking_id.carrier_tracking_ref:
                mapping_order_id = self.env["wk.order.mapping"].search([("erp_order_id", "=", picking_id.sale_id.id)])
                if mapping_order_id:
                    magento_configure_id = self.env["magento.configure"].search(
                        [("active", "=", True), ("state", "=", "enable")])
                    if magento_configure_id:
                        ctx.update({"instance_id": magento_configure_id.id})
                        connection = self.env["magento.configure"].with_context(ctx)._create_connection()
                        if connection:
                            url = connection[0]
                            token = connection[1]
                            url = "{}/index.php/rest/V1/acodesh/shipmenttracking/save".format(url)
                            payload = {"order_id": mapping_order_id.ecommerce_order_id,
                                       "company_name": picking_id.carrier_id.name,
                                       "tracking_number": picking_id.carrier_tracking_ref,
                                       "tracking_url": picking_id.carrier_tracking_url,
                                       }
                            headers = {
                                'authorization': token,
                                'Content-Type': 'application/json',
                            }
                            try:
                                response = requests.request("POST", url=url, data=json.dumps(payload), headers=headers)
                            except Exception as e:
                                raise Warning("{}".format(e))
                            if response:
                                if response.status_code == 200:
                                    response = json.loads(response.text)
                                    response = json.loads(response)
                                    if response.get("status"):
                                        status = "yes"
                                        text = "Tracking Information saved successfully"
                                    else:
                                        text = "Given Success but Tracking Information is not save"
                                else:
                                    text = "Error Message is {}".format(json.loads(response.text))
                            else:
                                text = "Error Message is {}".format(json.loads(response.text))
                        else:
                            text = "Something went wrong!!! Not connect to magento"
                    else:
                        text = "Not find the Magento Instance"
                else:
                    text = "Not Find sale order in mapping"
            else:
                text = "Not given Tracking Url or Tracking Number"
            self.env['magento.sync.history'].create(
                {'status': status, 'action_on': 'order', 'action': 'b', 'error_message': text})
            self._cr.commit()

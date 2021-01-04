import json
import logging
import uuid

import regex
import requests

from odoo import models, fields, _
from odoo.exceptions import Warning, ValidationError


def VALID_STRING(item): return (item not in [True, False, None]) and (len(item) > 1)


_logger = logging.getLogger(__name__)


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(selection_add=[('shipa_delivery', 'Shipa Delivery')])
    shipa_api_key = fields.Char(string="API Kay Id")
    shipa_payment_method = fields.Selection([('Prepaid', 'Prepaid'),
                                             ('CashOnDelivery', 'CashOnDelivery'),
                                             ('CCOD', 'CCOD')], string="Payment Methods",
                                            help="Choose Shipa Delivery Payment Methods")

    shipa_type_delivery = fields.Selection([('forward', 'forward'),
                                            ('reverse', 'reverse')], string="Type Of Delivery",
                                           help="Choose Shipa Delivery Type Delivery")

    shipa_print_mode = fields.Selection([('stream', 'stream'),
                                         ('attachment', 'attachment')], string="Print Mode",
                                        help="Choose Shipa Delivery print mode")

    shipa_print_template = fields.Selection([('standard', 'standard'),
                                             ('sticker-6x4', 'sticker-6x4'),
                                             ('international', 'international')], string="Print Template",
                                            help="Choose Shipa Delivery print Template")
    shipa_prod_url = fields.Char(string="Shipa URL", help="set url of the shipa delivery production environment API",
                                 default="https://api.shipadelivery.com/orders")
    shipa_test_url = fields.Char(string="Shipa URL", help="set url of the shipa delivery Sendbox environment API",
                                 default="https://sandbox-api.shipadelivery.com/orders")

    def shipa_delivery_send_shipping(self, pickings):
        for picking in pickings:
            if self.prod_environment:
                url = self.shipa_prod_url + "?apikey=" + self.shipa_api_key

            else:
                url = self.shipa_test_url + "?apikey=" + self.shipa_api_key

            shipper_address = picking.company_id
            recipient_address = picking.partner_id

            request_body = []
            cod_amount = 0.0

            shipa_payment_method = self.shipa_payment_method
            # if (pickings.sale_id.payment_gateway_id and pickings.sale_id.payment_gateway_id.code in ["cod", "COD"]) or (
            #         pickings.sale_id.eg_magento_payment_method_id and pickings.sale_id.eg_magento_payment_method_id.code in [
            #     "cod", "COD"]):
            if (pickings.sale_id.eg_magento_payment_method_id and pickings.sale_id.eg_magento_payment_method_id.code in [
                "cod", "COD"]):
                if not pickings.invoice_id.residual and self.env.user.has_group('eg_send_to_shipper.send_to_shipper_restriction'):
                    raise ValidationError("Shipment Can not be created with 0 COD amount!!!")
                shipa_payment_method = "CashOnDelivery"
                cod_amount = pickings.invoice_id.residual

            final_city = ""
            for t in recipient_address.city.split():
                result = regex.sub(u'[^\p{Latin}]', u'', t)
                if final_city:
                    final_city = final_city + " " + result
                else:
                    final_city = result
            final_city = final_city.strip()
            if not final_city:
                raise ValidationError("Recipient City is missing or No english Character")

            mobile_number = recipient_address.mobile or recipient_address.phone
            if not mobile_number:
                if pickings.partner_id.parent_id:
                    mobile_number = pickings.partner_id.parent_id.mobile or pickings.partner_id.parent_id.phone
                else:
                    raise ValidationError('There is no Mobile or Phone number in shipping address!')
            if mobile_number:
                # mobile_number.replace("+","") #Sahil Navadiya remove this & added below line
                mobile_number = mobile_number.split('+', 1)[-1]  # remove all characters before '+' including '+'

            else:
                raise ValidationError('There is no Mobile or Phone number in shipping address!')

            address_one = recipient_address.street or ""
            address_two = recipient_address.street2 or ""
            address_three = recipient_address.city or ""
            address_four = recipient_address.zip or ""

            body = {
                "id": "{}-{}".format(picking.name, str(uuid.uuid4())),
                "amount": cod_amount,
                "paymentMethod": "%s" % shipa_payment_method,
                "description": picking.origin,
                "typeDelivery": "%s" % self.shipa_type_delivery,
                "sender": {
                    "email": shipper_address.email,
                    "phone": shipper_address.phone,
                    "address": shipper_address.street,
                    "name": shipper_address.name
                },
                "recipient": {
                    "name": recipient_address.name,
                    "phone": mobile_number.replace(" ", ""),
                    "address": ','.join(filter(VALID_STRING, [address_one, address_two, address_three, address_four])),
                    "city": final_city
                }
                # "goodsValue": cod_amount
            }
            request_body.append(body)

            payload = json.dumps(request_body)
            headers = {"Accept": "application/json",
                       'Content-Type': "application/json"}
            try:
                _logger.info("Shipa Delivery Request Data : {}".format(payload))
                response_body = requests.request("POST", url, data=payload, headers=headers)
                if response_body.status_code == 200:
                    results = response_body.json()
                    _logger.info("Shipa Delivery Rate Response Data : {}".format(results))
                    final_tracking_no = []
                    for result in results:
                        tracking_no = result.get("deliveryInfo").get("reference")
                        final_tracking_no.append(tracking_no)
                    self.get_shipa_label(final_tracking_no, picking)
                    return [{'exact_price': 0.0,
                             'tracking_number': ','.join(final_tracking_no)}]
                else:
                    raise Warning("%s" % response_body.text)
            except Exception as e:
                raise Warning(e)

    def get_shipa_label(self, reference_id, picking):
        for ref_id in reference_id:
            if self.prod_environment:
                url = self.shipa_prod_url + "/" + ref_id + "/pdf?apikey=" + self.shipa_api_key + "&mode=" + self.shipa_print_mode + "&template=" + self.shipa_print_template + "&copies=1"
            else:
                url = self.shipa_test_url + "/" + ref_id + "/pdf?apikey=" + self.shipa_api_key + "&mode=" + self.shipa_print_mode + "&template=" + self.shipa_print_template + "&copies=1"
            headers = {"Accept": "application/json"}
            try:
                _logger.info("Shipa Delivery label Request Data %s" % url)
                response_body = requests.request("GET", url, headers=headers)
                _logger.info(["==============", response_body])
                if response_body.status_code == 200:
                    label = response_body.content
                    message_eg = (
                            _("Label generated!<br/> <b>Shipment Tracking Number : </b>%s") % ref_id)
                    picking.message_post(body=message_eg, attachments=[
                        ('Shipa Label%s.pdf' % ref_id, label)])
            except Exception as e:
                raise Warning(e)

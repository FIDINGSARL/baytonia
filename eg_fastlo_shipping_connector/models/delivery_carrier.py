import binascii
import http.client
import json
import logging

import regex
import requests

from odoo import models, fields, _
from odoo.exceptions import Warning, ValidationError


def VALID_STRING(item): return (item not in [True, False, None]) and (len(item) > 1)


_logger = logging.getLogger(__name__)


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(selection_add=[('fastlo_delivery', 'Fastlo Delivery')])
    fastlo_api_key = fields.Char(string="API Key")

    def fastlo_delivery_send_shipping(self, pickings):
        for picking in pickings:

            url = "https://fastlo.com/api/v1/add_shipment"

            shipper_address = picking.company_id
            recipient_address = picking.partner_id

            cod_amount = 0.0
            # if (pickings.sale_id.payment_gateway_id and pickings.sale_id.payment_gateway_id.code in ["cod", "COD"]) or (
            #         pickings.sale_id.eg_magento_payment_method_id and pickings.sale_id.eg_magento_payment_method_id.code in [
            #     "cod", "COD"]):
            if (pickings.sale_id.eg_magento_payment_method_id and pickings.sale_id.eg_magento_payment_method_id.code in [
                "cod", "COD"]):
                if not pickings.invoice_id.residual:
                    raise ValidationError("Shipment Can not be created with 0 COD amount!!!")
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
                mobile_number = mobile_number.split('+', 1)[-1]  # remove all characters before '+' including '+'

            else:
                raise ValidationError('There is no Mobile or Phone number in shipping address!')
            recipient_phone = ""
            sender_phone = ""
            if shipper_address.phone:
                dst_number = shipper_address.phone
                dst_number = dst_number.lstrip("0")
                dst_number = dst_number.lstrip("+")
                dst_number = dst_number.lstrip("966")
                sender_phone = "0{}".format(dst_number)

            if recipient_address.phone:
                dst_number = recipient_address.phone
                dst_number = dst_number.lstrip("0")
                dst_number = dst_number.lstrip("+")
                dst_number = dst_number.lstrip("966")
                recipient_phone = "0{}".format(dst_number)

            body = {
                'request': {
                    'sender_address': {
                        'sender_name': shipper_address.name,
                        'sender_mobile1': sender_phone or shipper_address.phone,
                        'sender_mobile2': '',
                        'sender_country': shipper_address.country_id.code,
                        'sender_city': shipper_address.city,
                        'sender_area': shipper_address.street,
                        'sender_street': shipper_address.street,
                        'sender_additional': '',
                        'sender_latitude': '',
                        'sender_longitude': ''
                    },
                    'receiver_address': {
                        'receiver_name': recipient_address.name,
                        'receiver_mobile1': recipient_phone or recipient_address.phone,
                        'receiver_mobile2': '',
                        'receiver_country': recipient_address.country_id.code,
                        'receiver_city': recipient_address.city,
                        'receiver_area': recipient_address.street,
                        'receiver_street': recipient_address.street,
                        'receiver_additional': '',
                        'receiver_latitude': '',
                        'receiver_longitude': ''
                    },
                    'shipment_data': {
                        'collect_cash_amount': cod_amount,
                        'number_of_pieces': 1,
                        'reference': picking.name
                    }
                }
            }

            payload = json.dumps(body)

            try:
                conn = http.client.HTTPSConnection("fastlo.com")
                headers = {
                    'Content-Type': 'application/json',
                    'fastlo-api-key': self.fastlo_api_key
                }
                _logger.info("Fastlo Delivery Request Data : {}".format(payload))
                conn.request("POST", "/api/v1/add_shipment", payload, headers)
                res = conn.getresponse()
                if res.status == 200:
                    data = res.read()
                    _logger.info("Fastlo Delivery Request Data : {}".format(data))
                    results = json.loads(data.decode('utf-8'))
                    _logger.info("Fastlo Delivery Response Data : {}".format(results))
                    final_tracking_no = []
                    tracking_no = results.get('output') and results.get('output').get("tracknumber")
                    if tracking_no:
                        final_tracking_no.append(tracking_no)
                        self.get_fastlo_label(final_tracking_no, picking)
                        return [{'exact_price': 0.0,
                                 'tracking_number': final_tracking_no[0]}]
                else:
                    raise Warning("%s" % res.read())
            except Exception as e:
                raise Warning(e)

    def get_fastlo_label(self, reference_id, picking):
        for ref_id in reference_id:
            conn = http.client.HTTPSConnection("fastlo.com")
            body = {
                "request": {
                    "tracknumber": ref_id,
                    "pdf_format": "base64",
                    "label_size": "4in_2in",
                    "optional_barcode": "none"
                }
            }
            payload = json.dumps(body)
            headers = {
                'Content-Type': 'application/json',
                'fastlo-api-key': 'c8da4153ebe46167b7a7145650605c19bua79yfzkxnsp0ita4eha86t1lcwjlzh'
            }

            try:
                _logger.info(["Fastlo Delivery label Generation Request Data %s" % payload])
                conn.request("POST", "/api/v1/label_shipment", payload, headers)
                res = conn.getresponse()
                if res.status == 200:
                    data = res.read()
                    results = json.loads(data.decode('utf-8'))
                    _logger.info(["Fastlo Delivery label Generation Response Data %s" % results])
                    label_data = results.get('output').get('shipment_label')
                    if label_data:
                        label = binascii.a2b_base64(str(label_data))
                        message_eg = (
                                _("Label generated!<br/> <b>Shipment Tracking Number : </b>%s") % ref_id)
                        picking.message_post(body=message_eg, attachments=[
                            ('Fastlo Label%s.pdf' % ref_id, label)])
                    else:
                        raise Warning("%s" % results)

                else:
                    raise Warning("%s" % res.read())

            except Exception as e:
                raise Warning(e)

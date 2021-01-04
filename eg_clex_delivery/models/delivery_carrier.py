import base64
import binascii
import json
import logging
import time
import uuid

import regex
import requests

from odoo import models, fields, _
from odoo.exceptions import Warning, ValidationError


def VALID_STRING(item): return (item not in [True, False, None]) and (len(item) > 1)


_logger = logging.getLogger(__name__)


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(selection_add=[('clex_delivery', 'CLEX Delivery')])
    clex_access_token = fields.Char(string="Access Token")
    clex_delivery_type = fields.Selection([('delivery', 'delivery'), ('self pickup', 'self pickup')])
    clex_package_height = fields.Integer(string="Package Height", help="set Height of Clax package")
    clex_package_width = fields.Integer(string="Package Width", help="set Width of Clax package")
    clex_package_depth = fields.Integer(string="Package Depth", help="set Depth of Clax package")

    def clex_delivery_send_shipping(self, pickings):
        for picking in pickings:
            if self.prod_environment:
                url = "https://api.clexsa.com/consignment/add"

            else:
                url = "https://stageapi.myboxee.net/consignment/add"
            shipper_address = picking.company_id
            recipient_address = picking.partner_id

            cod_amount = 0.0
            clex_billing_type = ""
            # if (pickings.sale_id.payment_gateway_id and pickings.sale_id.payment_gateway_id.code in ["cod", "COD"]) or (
            #         pickings.sale_id.eg_magento_payment_method_id and pickings.sale_id.eg_magento_payment_method_id.code in [
            #     "cod", "COD"]):
            if (
                    pickings.sale_id.eg_magento_payment_method_id and pickings.sale_id.eg_magento_payment_method_id.code in [
                "cod", "COD"]):
                if not pickings.invoice_id.residual and self.env.user.has_group(
                        'eg_send_to_shipper.send_to_shipper_restriction'):
                    raise ValidationError("Shipment Can not be created with 0 COD amount!!!")
                clex_billing_type = "COD"
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
            if not recipient_address.email:
                raise ValidationError('There is no Email in shipping address!')
            # cod_amount = 152
            if clex_billing_type == "COD" and cod_amount <= 0 and self.env.user.has_group(
                    'eg_send_to_shipper.send_to_shipper_restriction'):
                raise ValidationError('Required COD amount more then 0.0 while using COD service')
            body = {
                "shipment_reference_number": "{} ## {}".format(picking.origin, str(uuid.uuid4())),
                "shipment_type": "%s" % self.clex_delivery_type,
                "billing_type": "COD" if clex_billing_type == "COD" else "PRE PAID",
                "collect_amount": "%s" % cod_amount if clex_billing_type == "COD" else "0.0",
                "primary_service": "%s" % self.clex_delivery_type,
                "secondary_service": "Insurance-COD",
                "item_value": "%s" % cod_amount if clex_billing_type == "COD" else "0.0",
                "consignor": shipper_address.name,
                "consignor_email": shipper_address.email,
                "origin_city": shipper_address.city,
                "origin_area_new": "",
                "consignor_street_name": shipper_address.street,
                "consignor_address_two": "",
                "consignor_address_house_appartment": "",
                "consignor_address_landmark": "",
                "consignor_country_code": shipper_address.country_id.code,
                "consignor_phone": shipper_address.phone,
                "consignee": recipient_address.name,
                "consignee_email": recipient_address.email,
                "destination_city": final_city,
                "destination_area_new": "",
                "consignee_street_name": recipient_address.street,
                "consignee_address_two": "",
                "consignee_address_house_appartment": "",
                "consignee_address_landmark": "",
                "consignee_country_code": recipient_address.country_id.code,
                "consignee_phone": mobile_number,
                "pieces_count": str(picking.boxes),
                "order_date": "%s" % time.strftime("%d-%m-%Y"),
                "commodity_description": "",
                "pieces": [{"weight_actual": int(picking.shipping_weight),
                            "volumetric_width": "%s" % self.clex_package_width,
                            "volumetric_height": "%s" % self.clex_package_height,
                            "volumetric_depth": "%s" % self.clex_package_depth}]
            }
            payload = json.dumps(body)
            headers = {'Content-Type': "application/json",
                       "Access-token": self.clex_access_token}
            try:
                _logger.info("CLEX Delivery Request Data : {}".format(payload))
                response_body = requests.request("POST", url, data=payload, headers=headers)
                if response_body.status_code == 200:
                    results = response_body.json()
                    _logger.info("CLEX Delivery Rate Response Data : {}".format(results))
                    final_tracking_no = []
                    tracking_no = results.get('data') and results.get('data').get("0") and results.get('data').get(
                        "0").get('cn_id')
                    if tracking_no:
                        final_tracking_no.append(tracking_no)
                        self.get_clex_label(final_tracking_no, picking)
                        return [{'exact_price': 0.0,
                                 'tracking_number': final_tracking_no[0]}]
                    else:
                        raise Warning("%s" % response_body.text)
                else:
                    raise Warning("%s" % response_body.text)
            except Exception as e:
                raise Warning(e)

    def clex_delivery_return_send_shipping(self, sale_ids):
        for sale_id in sale_ids:
            if self.prod_environment:
                url = "https://api.clexsa.com/consignment/add"

            else:
                url = "https://stageapi.myboxee.net/consignment/add"

            shipper_address = sale_id.partner_id
            recipient_address = sale_id.company_id

            cod_amount = 0.0
            clex_billing_type = ""
            final_city = ""
            for t in shipper_address.city.split():
                result = regex.sub(u'[^\p{Latin}]', u'', t)
                if final_city:
                    final_city = final_city + " " + result
                else:
                    final_city = result
            final_city = final_city.strip()
            if not final_city:
                raise ValidationError("Recipient City is missing or No english Character")

            mobile_number = recipient_address.phone
            if not mobile_number:
                if sale_id.partner_id.parent_id:
                    mobile_number = sale_id.partner_id.parent_id.mobile or sale_id.partner_id.parent_id.phone
                else:
                    raise ValidationError('There is no Mobile or Phone number in shipping address!')
            if mobile_number:
                mobile_number = mobile_number.split('+', 1)[-1]  # remove all characters before '+' including '+'

            else:
                raise ValidationError('There is no Mobile or Phone number in shipping address!')
            if not recipient_address.email:
                raise ValidationError('There is no Email in shipping address!')
            # cod_amount = 152
            if clex_billing_type == "COD" and cod_amount <= 0 and self.env.user.has_group(
                    'eg_send_to_shipper.send_to_shipper_restriction'):
                raise ValidationError('Required COD amount more then 0.0 while using COD service')
            body = {
                "shipment_reference_number": "{} ## {}".format(sale_id.name, str(uuid.uuid4())),
                "shipment_type": "%s" % self.clex_delivery_type,
                "billing_type": "COD" if clex_billing_type == "COD" else "PRE PAID",
                "collect_amount": "%s" % cod_amount if clex_billing_type == "COD" else "0.0",
                "primary_service": "%s" % self.clex_delivery_type,
                "secondary_service": "Insurance-COD",
                "item_value": "%s" % cod_amount if clex_billing_type == "COD" else "0.0",
                "consignor": shipper_address.name,
                "consignor_email": shipper_address.email,
                "origin_city": final_city,
                "origin_area_new": "",
                "consignor_street_name": shipper_address.street,
                "consignor_address_two": "",
                "consignor_address_house_appartment": "",
                "consignor_address_landmark": "",
                "consignor_country_code": shipper_address.country_id.code,
                "consignor_phone": shipper_address.phone,
                "consignee": recipient_address.name,
                "consignee_email": recipient_address.email,
                "destination_city": recipient_address.city,
                "destination_area_new": "",
                "consignee_street_name": recipient_address.street,
                "consignee_address_two": "",
                "consignee_address_house_appartment": "",
                "consignee_address_landmark": "",
                "consignee_country_code": recipient_address.country_id.code,
                "consignee_phone": mobile_number,
                "pieces_count": '1',
                "order_date": "%s" % time.strftime("%d-%m-%Y"),
                "commodity_description": "",
                "pieces": [{"weight_actual": 2,
                            "volumetric_width": "%s" % self.clex_package_width,
                            "volumetric_height": "%s" % self.clex_package_height,
                            "volumetric_depth": "%s" % self.clex_package_depth}]
            }
            payload = json.dumps(body)
            headers = {'Content-Type': "application/json",
                       "Access-token": self.clex_access_token}
            try:
                _logger.info("CLEX Delivery Request Data : {}".format(payload))
                response_body = requests.request("POST", url, data=payload, headers=headers)
                if response_body.status_code == 200:
                    results = response_body.json()
                    _logger.info("CLEX Delivery Rate Response Data : {}".format(results))
                    final_tracking_no = []
                    tracking_no = results.get('data') and results.get('data').get("0") and results.get('data').get(
                        "0").get('cn_id')
                    if tracking_no:
                        final_tracking_no.append(tracking_no)
                        self.get_clex_label(final_tracking_no, sale_id)
                        sale_id.return_carrier_id = self.id
                        sale_id.return_tracking_ref = final_tracking_no[0]
                    else:
                        raise Warning("%s" % response_body.text)
                else:
                    raise Warning("%s" % response_body.text)
            except Exception as e:
                raise Warning(e)

    def get_clex_label(self, reference_id, picking):
        for ref_id in reference_id:
            url = "http://cockpit.clexsa.com/pdf/download/%s?id=%s&type=A4-consignment_clex_label&return_type=pdf" % (
                ref_id, ref_id)
        headers = {"Content-Type": "application/json",
                   "Access-token": self.clex_access_token}
        try:
            response_body = requests.request("POST", url, headers=headers)
            if response_body.status_code == 200:
                results = response_body.json()
                _logger.info(["CLEX Delivery label Generation Response Data %s" % results])
                label_url = results.get('data').get('awb_pdf_url')
                if label_url:
                    label = binascii.a2b_base64((base64.b64encode(requests.get(label_url).content)).decode('utf-8'))
                    message_eg = (
                            _("Label generated!<br/> <b>Shipment Tracking Number : </b>%s") % ref_id)
                    picking.message_post(body=message_eg, attachments=[
                        ('CLEX Label%s.pdf' % ref_id, label)])
                else:
                    raise Warning("%s" % response_body.text)

            else:
                raise Warning("%s" % response_body.text)

        except Exception as e:
            raise Warning(e)

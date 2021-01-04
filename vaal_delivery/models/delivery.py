# -*- coding: utf-8 -*-
# Part of eComBucket. See LICENSE file for full copyright and licensing details.
import json
import logging

import regex
import requests

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

# BASE = "https://api.vaal.me/api"
BASE = "https://deliver.vaal.me/ords/vaal/api/v2"


def VALID_STRING(item): return (item not in [True, False, None]) and (len(item) > 1)


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"
    delivery_type = fields.Selection(
        selection_add=[('vaal', 'VAAL')]
    )
    vaal_username = fields.Char(
        string='User Name',
        default='BAYTONIA'
    )
    vaal_password = fields.Char(
        string='Password',
        default='123Bayt'
    )

    def vaal_rate_shipment(self, order):
        return self.base_on_rule_rate_shipment(order)

    def get_vaal_client_token(self):
        # _logger.info("\n\n--- %s\n",self.vaal_username)
        data = {'grant_type': 'client_credentials'}
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        x = requests.post('https://deliver.vaal.me/ords/vaal/oauth/token',
                          data=data,
                          auth=('fO3cCHpjWKi2F4Ut8c_vcQ..', 'nkMsw9yEdbUndpxoSxendA..'),
                          headers=headers).json()
        return (x or {}).get('access_token')

    @api.model
    def get_vaal_headers(self, add_auth=True):
        headers = {'Content-Type': 'Application/json'}
        if add_auth:
            headers['Authorization'] = "Bearer %s" % (self.get_vaal_client_token())
        _logger.info("%r" % headers)

        return headers

    @api.one
    def vaal_send_shipping(self, pickings):

        refrence = pickings.origin or pickings.name
        data = self._get_item_data(pickings=pickings, uom_id=pickings.weight_uom_id)

        c_addrs = self.get_shipment_recipient_address(picking=pickings)
        cName = c_addrs.get("name")
        cCity = c_addrs.get("city")
        cZip = c_addrs.get("zip")
        cMobile = c_addrs.get("mobile")
        cAddr1 = c_addrs.get("street")
        cAddr2 = c_addrs.get("street2")

        final_city = ""
        for t in cCity.split():
            result = regex.sub(u'[^\p{Latin}]', u'', t)
            if final_city:
                final_city = final_city + " " + result
            else:
                final_city = result
        cCity = final_city
        # print(cCity)

        # order  = self.env['sale.order'].search([('name','=',pickings.origin)],limit=1)
        # Note: To take amount from newly generated invoice
        cod_amount = 0
        # if (pickings.sale_id.payment_gateway_id and pickings.sale_id.payment_gateway_id.code in ["cod", "COD"]) or (
        #         pickings.sale_id.eg_magento_payment_method_id and pickings.sale_id.eg_magento_payment_method_id.code in [
        #     "cod", "COD"]):

        if (pickings.sale_id.eg_magento_payment_method_id and pickings.sale_id.eg_magento_payment_method_id.code in [
            "cod", "COD"]):
            if not pickings.invoice_id.residual and self.env.user.has_group('eg_send_to_shipper.send_to_shipper_restriction'):
                raise ValidationError("Shipment Can not be created with 0 COD amount!!!")
            cod_amount = pickings.invoice_id.residual
        codAmt = cod_amount
        weight = data.get('weight') or self.default_product_weight

        mobile_number = c_addrs.get("mobile") or c_addrs.get("phone")
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

        api_post_data = {
            "drop_address": cCity.upper(),
            # "drop_address": ','.join(filter(VALID_STRING, [cAddr1,cAddr2,cCity,cZip])),
            "receiver_name": c_addrs.get("name") or "",
            "mobile_number": mobile_number.replace(" ", ""),
            "cod": codAmt,
            "details": ','.join(filter(VALID_STRING, [cAddr1, cAddr2, cCity, cZip])),
            "weight": weight,
            "additional_info": "Order refrence: %s" % refrence
        }
        # _logger.info("\n\nDATA : %s\n",api_post_data)
        headers = self.get_vaal_headers()
        # url = "{BASE}/orders".format(BASE=BASE)
        url = "https://deliver.vaal.me/ords/vaal/api/v2/orders/"
        response = requests.post(url, data=json.dumps({'orders': [api_post_data]}), headers=headers)
        # _logger.info("\n\nAPI POST DATA : %r\n"%api_post_data)
        _logger.info("\nResponse : %s", response.text)
        _logger.info("\n\n%r\n" % response)
        response = response.json()
        if isinstance(response, dict) and response.get('success') == False:
            raise ValidationError('%s' % response)

        # VAAL not support all city so raise error if not supported city
        for i in response.get('orders'):
            if i.get('status') == 'Drop address is not among defined cities':
                raise ValidationError(
                    'Drop address is not among defined cities.\n\n%s is not supported city' % (cCity.upper()))

        tracking_number = ','.join(['%s' % i.get('order_id') for i in response.get('orders') if i.get('status')])
        self.vaal_print_waybill(headers, tracking_number, codAmt, pickings)

        return {
            'exact_price': codAmt,
            # 'tracking_number':','.join(['%s' % i.get('order_id') for i in response.get('orders') if i.get('status')]),
            'tracking_number': tracking_number,
        }

    def vaal_print_waybill(self, headers, tracking_number, cod_amt, pickings):
        url = "https://deliver.vaal.me/ords/vaal/api/v2/orders/print/%s" % tracking_number
        res = requests.get(url, headers=headers)

        attachments = [(self.delivery_type + ' ' + str(tracking_number) + '.pdf', res.content)]
        pickings.message_post(body='Attachments of VAAL Waybill %s' % tracking_number, subject="Waybill",
                              attachments=attachments)

        track_url = "https://deliver.vaal.me/ords/f?p=VAAL:ORDER_TRACKING"
        order_currency = pickings.sale_id.currency_id or self.company_id.currency_id
        msg = _("Shipment sent to carrier %s for shipping with tracking number %s<br/>Cost: %.2f %s<br/><br/>%s") % (
            pickings.carrier_id.name,
            tracking_number,
            cod_amt,
            order_currency.name,
            track_url)

        pickings.sale_id.message_post(body=msg, subject="Waybill", attachments=attachments)

    def vaal_get_tracking_link(self, picking):
        order_id = picking.carrier_tracking_ref.split(',')[-1]
        if order_id:
            return "https://deliver.vaal.me/ords/f?p=VAAL:ORDER_TRACKING:::::ORDER_NO:%s" % order_id

    def vaal_cancel_shipment(self, pickings):
        # Sahil Navadiya : VAAL API not support cancel delivery order but in odoo we can
        # raise ValidationError("No API to cancel delivery.") #Old code by ecom
        _logger.warning("\nThere is no API for cancel order for VAAL\n")

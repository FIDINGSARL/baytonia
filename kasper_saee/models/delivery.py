# -*- coding: utf-8 -*-
# Part of Futurelens Studio. See LICENSE file for full copyright and licensing details.

import logging

import pdfkit
import regex
import requests

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, Warning

_logger = logging.getLogger(__name__)


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(selection_add=[('saee', 'SAEE')])
    saee_secret = fields.Char(string='Secret Key')
    saee_test = fields.Char(string='Test URL', default="http://www.k-w-h.com/deliveryrequest/")
    saee_live = fields.Char(string='Live URL', default="http://www.saee.sa/deliveryrequest/")

    def saee_rate_shipment(self, order):
        return self.base_on_rule_rate_shipment(order)

    def get_base_url(self, pickings):
        if pickings and pickings.carrier_id.delivery_type == "saee":
            carrier_id = pickings.carrier_id
        else:
            carrier_id = self.env['delivery.carrier'].search([('delivery_type', '=', 'saee')], limit=1)

        if not carrier_id:
            raise ValidationError('No configuration found for Kasper Saee Delivery Method/Carrier!')

        if carrier_id.prod_environment:
            base_url = carrier_id.saee_live
        else:
            base_url = carrier_id.saee_test
        if base_url.endswith('/'):
            return base_url
        else:
            return "%s/" % base_url

    @api.one
    def saee_send_shipping(self, pickings):
        base_url = self.get_base_url(pickings)

        cod_amount = 0.0
        # if (pickings.sale_id.payment_gateway_id and pickings.sale_id.payment_gateway_id.code in ["cod", "COD"]) or (
        #         pickings.sale_id.eg_magento_payment_method_id and pickings.sale_id.eg_magento_payment_method_id.code in [
        #     "cod", "COD"]):

        if (pickings.sale_id.eg_magento_payment_method_id and pickings.sale_id.eg_magento_payment_method_id.code in [
            "cod", "COD"]):
            if not pickings.invoice_id.residual and self.env.user.has_group('eg_send_to_shipper.send_to_shipper_restriction'):
                raise ValidationError("Shipment Can not be created with 0 COD amount!!!")
            cod_amount = pickings.invoice_id.residual
        # if pickings.sale_id.payment_gateway_id and pickings.sale_id.payment_gateway_id.code in ["cod", "COD"]:
        #     # cod_amount = pickings.sale_id.amount_total
        #     #
        #     # for inv in self.env['account.invoice'].search([('origin', '=', pickings.sale_id.name)]):
        #     #     if inv.state == "paid":
        #     #         cod_amount = cod_amount - inv.amount_total
        #     #     elif inv.state == "open":
        #     #         if inv.amount_total != inv.residual and inv.residual > 0:
        #     #             cod_amount = cod_amount - (inv.amount_total - inv.residual)
        #     # Note: To take amount from newly generated invoice
        #     cod_amount = pickings.invoice_id.residual


        if pickings and pickings.carrier_id.delivery_type == "saee":
            carrier_id = pickings.carrier_id
        else:
            carrier_id = self.env['delivery.carrier'].search([('delivery_type', '=', 'saee')], limit=1)

        headers = {'Content-Type': "application/json;charset=utf-8"}
        partner_id = pickings.partner_id

        mobile = partner_id.mobile or partner_id.phone
        if not mobile:
            mobile = partner_id.parent_id.mobile or partner_id.parent_id.phone

        mobile2 = partner_id.phone or partner_id.mobile
        if not mobile2:
            mobile2 = partner_id.parent_id.phone or partner_id.parent_id.mobile

        c_city = partner_id.city or ''

        final_city = ""
        for t in c_city.split():
            result = regex.sub(u'[^\p{Latin}]', u'', t)
            if final_city:
                final_city = final_city + " " + result
            else:
                final_city = result
        c_city = final_city

        payload = {
            "secret": carrier_id.saee_secret or False,
            "ordernumber": pickings.origin or '',
            "cashondelivery": cod_amount,
            "name": partner_id.name,
            "mobile": mobile or '',
            "mobile2": mobile2 or '',
            "streetaddress": partner_id.street,
            "streetaddress2": partner_id.street2 or '',
            # "city":partner_id.city,
            "city": c_city,
            "state": partner_id.state_id.name,
            "zipcode": partner_id.zip or '',
            "weight": pickings.shipping_weight or 1.0,
            "quantity": pickings.number_of_packages or 1,
        }
        res = requests.post("%snew" % base_url, json=payload, headers=headers)
        res.raise_for_status()
        data_dict = res.json()
        waybill = data_dict.get("waybill", False)
        if not waybill:
            raise Warning("%s" % data_dict)
        self.saee_print_waybill(data_dict.get('waybill'), cod_amount, base_url, pickings)

        return {
            'exact_price': cod_amount,
            'tracking_number': data_dict.get('waybill'),
        }

    def saee_get_tracking_link(self, pickings):
        # API URL : http://www.k-w-h.com/tracking?trackingnum=OS00087823KS
        if pickings and pickings.carrier_id.delivery_type == "saee":
            carrier_id = pickings.carrier_id
            if carrier_id.prod_environment:
                return "http://www.saee.sa/trackingpage?trackingnum=%s" % pickings.carrier_tracking_ref
            else:
                return "http://www.k-w-h.com/trackingpage?trackingnum=%s" % pickings.carrier_tracking_ref

    def saee_cancel_shipment(self, pickings):
        if pickings and pickings.carrier_id.delivery_type == "saee":
            carrier_id = pickings.carrier_id
        else:
            carrier_id = self.env['delivery.carrier'].search([('delivery_type', '=', 'saee')], limit=1)

        base_url = self.get_base_url(pickings)
        headers = {'Content-Type': "application/json"}
        base_url = "%scancel?secret=%s&waybill=%s" % (
            base_url, carrier_id.saee_secret or False, pickings.carrier_tracking_ref)
        res = requests.post(base_url, headers=headers)

        res.raise_for_status()
        if res.text == '1':
            body = 'Shipment with Kasper Saee is cancelled'
        else:
            raise ValidationError('Failed to cancel shipment %s with Kasper Saee' % pickings.carrier_tracking_ref)

    def saee_print_waybill(self, tracking_number, cod_amt, base_url, pickings):
        if base_url is False:
            base_url = self.get_base_url(pickings)

        base_url = "%sprintsticker/%s" % (base_url, tracking_number)
        pdf = pdfkit.from_url(base_url, False)
        attachments = [(self.delivery_type + ' ' + str(tracking_number) + '.pdf', pdf)]
        pickings.message_post(body='Attachments of KASPER Waybill %s' % tracking_number, subject="Waybill",
                              attachments=attachments)

        order_currency = pickings.sale_id.currency_id or self.company_id.currency_id
        msg = _("Shipment sent to carrier %s for shipping with tracking number %s<br/>Cost: %.2f %s<br/><br/>%s") % (
            pickings.carrier_id.name,
            tracking_number,
            cod_amt,
            order_currency.name,
            self.saee_get_tracking_link(pickings))

        pickings.sale_id.message_post(body=msg, subject="Waybill", attachments=attachments)

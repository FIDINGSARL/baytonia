# -*- coding: utf-8 -*-
# Part of eComBucket. See LICENSE file for full copyright and licensing details.
import logging

try:
    from zeep import Client
except Exception as e:
    pass

import regex
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(selection_add=[('smsa', 'SMSA')])
    smsa_ship_type = fields.Char(string='Ship Type')
    smsa_pass_key = fields.Char(string='Key')
    smsa_sequence_id = fields.Many2one('ir.sequence', string='Label Sequence')

    def smsa_rate_shipment(self, order):
        return self.base_on_rule_rate_shipment(order)

    @staticmethod
    def get_smsa_client():
        uri = "http://track.smsaexpress.com/SECOM/SMSAwebService.asmx?WSDL"
        return Client(uri)

    @api.one
    def smsa_send_shipping(self, pickings):

        attachments = []
        tracking_numbers = []
        client = self.get_smsa_client()
        passKey = self.smsa_pass_key
        refrence = pickings.origin or pickings.name
        refNo = '%s_%s' % (refrence, self.smsa_sequence_id.next_by_id())  # fields.DateTime.now()
        currency = "1"  # self.get_shipment_currency_id(pickings=pickings)
        data = self._get_item_data(pickings=pickings, uom_id=pickings.weight_uom_id)
        # if currency:
        #     currency = currency.name
        # else:
        #     currency = ""
        c_addrs = self.get_shipment_recipient_address(picking=pickings)
        sentDate = ""
        idNo = pickings.origin or pickings.name

        cName = c_addrs.get("name") or ""
        cntry = ""
        cCity = c_addrs.get("city") or ""

        final_city = ""
        for t in cCity.split():
            result = regex.sub(u'[^\p{Latin}]', u'', t)
            if final_city:
                final_city = final_city + " " + result
            else:
                final_city = result
        cCity = final_city

        cZip = c_addrs.get("zip") or ""
        cPOBox = ""
        cMobile = c_addrs.get("mobile") or c_addrs.get("phone")
        cTel1 = c_addrs.get("phone") or c_addrs.get("mobile")

        cTel2 = ""

        if not cMobile:
            cMobile = pickings.partner_id.parent_id.mobile or pickings.partner_id.parent_id.phone
        if not cTel1:
            cTel1 = pickings.partner_id.parent_id.phone or pickings.partner_id.parent_id.mobile

        cAddr1 = c_addrs.get("street") or ""
        cAddr2 = c_addrs.get("street2") or ""

        shipType = self.smsa_ship_type
        # DLV,VAL,HAL or BLT
        PCs = str(pickings.boxes)
        addShipMPS = str(pickings.boxes)

        cEmail = c_addrs.get('email')
        carrValue = "1"
        carrCurr = currency
        order = self.env['sale.order'].search([('name', '=', pickings.origin)], limit=1)
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
        custVal = ""
        custCurr = currency

        insrAmt = data.get('amount')
        insrCurr = currency
        itemDesc = pickings.origin or pickings.name

        s_addrs = self.get_shipment_shipper_address(picking=pickings)
        sName = s_addrs.get('name') or ""
        sContact = s_addrs.get('name') or ""
        sAddr1 = s_addrs.get('street') or ""
        sAddr2 = s_addrs.get('street2') or ""
        sCity = s_addrs.get('city') or ""

        final_city = ""
        for t in sCity.split():
            result = regex.sub(u'[^\p{Latin}]', u'', t)
            if final_city:
                final_city = final_city + " " + result
            else:
                final_city = result
        sCity = final_city

        sPhone = (s_addrs.get("phone") or "").replace(" ", "").replace("+", "")
        sCntry = s_addrs.get('country_code')

        prefDelvDate = ""
        gpsPoints = ""
        data_dict = dict(passKey=passKey,
                         refNo=refNo, sentDate=sentDate, idNo=idNo,
                         cName=cName, cntry=cntry, cCity=cCity, cZip=cZip,
                         cPOBox=cPOBox, cMobile=cMobile, cTel1=cTel1, cTel2=cTel2,
                         cAddr1=cAddr1, cAddr2=cAddr2, PCs=PCs, shipType=shipType, cEmail=cEmail,
                         carrValue="%s" % carrValue, carrCurr="%s" % carrCurr, codAmt="%s" % codAmt,
                         weight="%s" % weight,
                         custVal="%s" % custVal, custCurr="%s" % custCurr, insrAmt="%s" % insrAmt,
                         insrCurr="%s" % insrCurr,
                         itemDesc=itemDesc, sName=sName, sContact=sContact, sAddr1=sAddr1, sAddr2=sAddr2,
                         sCity=sCity, sPhone=sPhone, sCntry=sCntry, prefDelvDate=prefDelvDate, gpsPoints=gpsPoints)
        if pickings.boxes > 1:
            awbNo = client.service.addShipMPS(
                passKey=passKey,
                refNo=refNo, sentDate=sentDate, idNo=idNo,
                cName=cName, cntry=cntry, cCity=cCity, cZip=cZip,
                cPOBox=cPOBox, cMobile=cMobile, cTel1=cTel1, cTel2=cTel2,
                cAddr1=cAddr1, cAddr2=cAddr2, PCs=PCs, shipType=shipType, cEmail=cEmail,
                carrValue="%s" % carrValue, carrCurr="%s" % carrCurr, codAmt="%s" % codAmt, weight="%s" % weight,
                custVal="%s" % custVal, custCurr="%s" % custCurr, insrAmt="%s" % insrAmt, insrCurr="%s" % insrCurr,
                itemDesc=itemDesc, sName=sName, sContact=sContact, sAddr1=sAddr1, sAddr2=sAddr2,
                sCity=sCity, sPhone=sPhone, sCntry=sCntry, prefDelvDate=prefDelvDate, gpsPoints=gpsPoints
            )
        else:
            awbNo = client.service.addShip(
                passKey=passKey,
                refNo=refNo, sentDate=sentDate, idNo=idNo,
                cName=cName, cntry=cntry, cCity=cCity, cZip=cZip,
                cPOBox=cPOBox, cMobile=cMobile, cTel1=cTel1, cTel2=cTel2,
                cAddr1=cAddr1, cAddr2=cAddr2, PCs=PCs, shipType=shipType, cEmail=cEmail,
                carrValue="%s" % carrValue, carrCurr="%s" % carrCurr, codAmt="%s" % codAmt, weight="%s" % weight,
                custVal="%s" % custVal, custCurr="%s" % custCurr, insrAmt="%s" % insrAmt, insrCurr="%s" % insrCurr,
                itemDesc=itemDesc, sName=sName, sContact=sContact, sAddr1=sAddr1, sAddr2=sAddr2,
                sCity=sCity, sPhone=sPhone, sCntry=sCntry, prefDelvDate=prefDelvDate, gpsPoints=gpsPoints
            )

        _logger.info("=========%r===%r===" % (awbNo, refNo))
        tracking = ""
        if awbNo:
            list_awb_no = awbNo.split(",")
            for awb_no in list_awb_no:
                tracking = "http://www.smsaexpress.com/Track.aspx?tracknumbers=%s" % awb_no
                try:
                    tracking_numbers.append(awb_no)
                    res = client.service.getPDF(awbNo=int(awb_no), passKey=passKey)
                    attachments.append((self.delivery_type + ' ' + str(awb_no) + '.pdf', res))
                except Exception as e:
                    raise ValidationError(awb_no)

        pickings.message_post(
            body=tracking,
            subject="Attachments of tracking",
            attachments=attachments
        )

        order_currency = pickings.sale_id.currency_id or self.company_id.currency_id
        msg = _("Shipment sent to carrier %s for shipping with tracking number %s<br/>Cost: %.2f %s<br/><br/>%s") % (
            pickings.carrier_id.name,
            ','.join(tracking_numbers),
            codAmt,
            order_currency.name,
            tracking)

        pickings.sale_id.message_post(
            body=msg,
            subject="Attachments of tracking",
            attachments=attachments
        )

        return {
            'exact_price': codAmt,
            'tracking_number': ','.join(tracking_numbers),
        }

    def smsa_get_tracking_link(self, picking):
        client = self.get_smsa_client()
        res = client.service.getStatus(passkey=self.smsa_pass_key, awbNo=picking.carrier_tracking_ref)
        # res=client.service.getStatus(passkey = self.smsa_pass_key, awbNo=290029474753)
        picking.message_post(
            body='%s' % res,
            subject="Tracking details",
        )
        # resd = (res.__dict__)
        # (resd).pop('schema','')
        # resd1 = dict(resd).get('__values__') or dict()
        # (resd1).pop('schema','')

        raise ValidationError('%s' % res)

    def smsa_cancel_shipment(self, pickings):
        client = self.get_smsa_client()
        res = client.service.cancelShipment(passkey=self.smsa_pass_key, awbNo=pickings.carrier_tracking_ref,
                                            reas='Cancel Delivery')
        pickings.message_post(
            body='%s' % res,
            subject="Cancel details",
        )

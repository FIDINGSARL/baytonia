from odoo import models,fields,api, _
from odoo.exceptions import ValidationError

import requests
import logging
import regex
import pdfkit

_logger = logging.getLogger(__name__)


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

#This is not required as it is duplicating delivery label by sending twice to API, remove by Sahil Navadiya
#
#     def vaal_print_waybill(self, headers, tracking_number, pickings):
#         # headers = self.get_vaal_headers()
#         # base_url = "%sprintsticker/%s"%(base_url,pickings.carrier_tracking_ref)
#         url = "https://deliver.vaal.me/ords/vaal/api/v2/orders/print/%s" % (tracking_number)
#         # pdf = pdfkit.from_url(url, False)
#         res = requests.get(url, headers=headers)
# 
#         attachments = [(self.delivery_type + ' ' + str(tracking_number) + '.pdf', res.content)]
#         pickings.message_post(body='Attachments of VAAL Waybill %s' % (tracking_number), subject="Waybill",
#                               attachments=attachments)
#         pickings.sale_id.message_post(body='Attachments of VAAL Waybill %s' % (tracking_number), subject="Waybill",
#                               attachments=attachments)
# 
#     @api.one
#     def smsa_send_shipping(self, pickings):
# 
#         attachments = []
#         tracking_numbers = []
#         client = self.get_smsa_client()
#         passKey = self.smsa_pass_key
#         refrence = pickings.origin or pickings.name
#         refNo = '%s_%s' % (refrence, self.smsa_sequence_id.next_by_id())  # fields.DateTime.now()
#         currency = "1"  # self.get_shipment_currency_id(pickings=pickings)
#         data = self._get_item_data(pickings=pickings, uom_id=pickings.weight_uom_id)
#         # if currency:
#         #     currency = currency.name
#         # else:
#         #     currency = ""
#         c_addrs = self.get_shipment_recipient_address(picking=pickings)
#         sentDate = ""
#         idNo = pickings.origin or pickings.name
# 
#         cName = c_addrs.get("name") or ""
#         cntry = ""
#         cCity = c_addrs.get("city") or ""
# 
#         final_city = ""
#         for t in cCity.split():
#             result = regex.sub(u'[^\p{Latin}]', u'', t)
#             if final_city:
#                 final_city = final_city + " " + result
#             else:
#                 final_city = result
#         cCity = final_city
# 
#         cZip = c_addrs.get("zip") or ""
#         cPOBox = ""
#         cMobile = c_addrs.get("mobile") or c_addrs.get("phone")
#         cTel1 = c_addrs.get("phone") or c_addrs.get("mobile")
# 
#         cTel2 = ""
# 
#         if not cMobile:
#             cMobile = pickings.partner_id.parent_id.mobile or pickings.partner_id.parent_id.phone
#         if not cTel1:
#             cTel1 = pickings.partner_id.parent_id.phone or pickings.partner_id.parent_id.mobile
# 
#         cAddr1 = c_addrs.get("street") or ""
#         cAddr2 = c_addrs.get("street2") or ""
# 
#         shipType = self.smsa_ship_type
#         # DLV,VAL,HAL or BLT
#         PCs = "1"
# 
#         cEmail = c_addrs.get('email')
#         carrValue = "1"
#         carrCurr = currency
#         order = self.env['sale.order'].search([('name', '=', pickings.origin)], limit=1)
#         codAmt = data.get('amount')
#         weight = data.get('weight') or self.default_product_weight
#         custVal = ""
#         custCurr = currency
# 
#         insrAmt = data.get('amount')
#         insrCurr = currency
#         itemDesc = pickings.origin or pickings.name
# 
#         s_addrs = self.get_shipment_shipper_address(picking=pickings)
#         sName = s_addrs.get('name') or ""
#         sContact = s_addrs.get('name') or ""
#         sAddr1 = s_addrs.get('street') or ""
#         sAddr2 = s_addrs.get('street2') or ""
#         sCity = s_addrs.get('city') or ""
# 
#         final_city = ""
#         for t in sCity.split():
#             result = regex.sub(u'[^\p{Latin}]', u'', t)
#             if final_city:
#                 final_city = final_city + " " + result
#             else:
#                 final_city = result
#         sCity = final_city
# 
#         sPhone = (s_addrs.get("phone") or "").replace(" ", "").replace("+", "")
#         sCntry = s_addrs.get('country_code')
#         prefDelvDate = ""
#         gpsPoints = ""
#         data_dict = dict(passKey=passKey,
#                          refNo=refNo, sentDate=sentDate, idNo=idNo,
#                          cName=cName, cntry=cntry, cCity=cCity, cZip=cZip,
#                          cPOBox=cPOBox, cMobile=cMobile, cTel1=cTel1, cTel2=cTel2,
#                          cAddr1=cAddr1, cAddr2=cAddr2, PCs=PCs, shipType=shipType, cEmail=cEmail,
#                          carrValue="%s" % carrValue, carrCurr="%s" % carrCurr, codAmt="%s" % codAmt,
#                          weight="%s" % weight,
#                          custVal="%s" % custVal, custCurr="%s" % custCurr, insrAmt="%s" % insrAmt,
#                          insrCurr="%s" % insrCurr,
#                          itemDesc=itemDesc, sName=sName, sContact=sContact, sAddr1=sAddr1, sAddr2=sAddr2,
#                          sCity=sCity, sPhone=sPhone, sCntry=sCntry, prefDelvDate=prefDelvDate, gpsPoints=gpsPoints)
#         awbNo = client.service.addShip(
#             passKey=passKey,
#             refNo=refNo, sentDate=sentDate, idNo=idNo,
#             cName=cName, cntry=cntry, cCity=cCity, cZip=cZip,
#             cPOBox=cPOBox, cMobile=cMobile, cTel1=cTel1, cTel2=cTel2,
#             cAddr1=cAddr1, cAddr2=cAddr2, PCs=PCs, shipType=shipType, cEmail=cEmail,
#             carrValue="%s" % carrValue, carrCurr="%s" % carrCurr, codAmt="%s" % codAmt, weight="%s" % weight,
#             custVal="%s" % custVal, custCurr="%s" % custCurr, insrAmt="%s" % insrAmt, insrCurr="%s" % insrCurr,
#             itemDesc=itemDesc, sName=sName, sContact=sContact, sAddr1=sAddr1, sAddr2=sAddr2,
#             sCity=sCity, sPhone=sPhone, sCntry=sCntry, prefDelvDate=prefDelvDate, gpsPoints=gpsPoints
#         )
#         _logger.info("=========%r===%r===" % (awbNo, refNo))
#         tracking = ""
#         if awbNo:
#             tracking = "http://www.smsaexpress.com/Track.aspx?tracknumbers=%s" % awbNo
#             try:
#                 tracking_numbers.append(awbNo)
#                 res = client.service.getPDF(awbNo=int(awbNo), passKey=passKey)
#                 attachments.append((self.delivery_type + ' ' + str(awbNo) + '.pdf', res))
#             except Exception as e:
#                 raise ValidationError(awbNo)
# 
#         pickings.message_post(
#             body=tracking,
#             subject="Attachments of tracking",
#             attachments=attachments
#         )
#         pickings.sale_id.message_post(
#             body=tracking,
#             subject="Attachments of tracking",
#             attachments=attachments
#         )
#         return {
#             'exact_price': codAmt,
#             'tracking_number': ','.join(tracking_numbers),
#         }
# 
#     def saee_print_waybill(self, tracking_number, base_url, pickings):
#         if base_url is False:
#             base_url = self.get_base_url(pickings)
# 
#         # base_url = "%sprintsticker/%s"%(base_url,pickings.carrier_tracking_ref)
#         base_url = "%sprintsticker/%s" % (base_url, tracking_number)
#         pdf = pdfkit.from_url(base_url, False)
#         attachments = [(self.delivery_type + ' ' + str(tracking_number) + '.pdf', pdf)]
#         pickings.message_post(body='Attachments of KASPER Waybill %s' % (tracking_number), subject="Waybill",
#                               attachments=attachments)
#         pickings.sale_id.message_post(body='Attachments of KASPER Waybill %s' % (tracking_number), subject="Waybill",
#                               attachments=attachments)
# 
# 
# 



# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################


from odoo import api, fields, models
from odoo.exceptions import UserError


Carrier_Code = [
    ('custom', 'Custom Value'),
    ('dhl', 'DHL'),
    ('fedex', 'Federal Express'),
    ('ups', 'United Parcel Service'),
    ('usps', 'United States Postal Service'),
    ('temando', 'Magento Shipping')
]


class StockPicking(models.Model):
    _inherit = "stock.picking"

    carrier_code = fields.Selection(
        Carrier_Code,
        string='Magento Carrier',
        default="custom",
        help="Magento Carrier")
    magento_shipment = fields.Char(
        string='Magento Shipment',
        help="Contains Magento Order Shipment Number (eg. 300000008)")


    @api.multi
    def action_sync_tracking_no(self):
        text = ''
        ctx = dict(self._context or {})
        for pickingObj in self:
            saleId = pickingObj.sale_id.id
            mageShipment = pickingObj.magento_shipment
            carrierCode = pickingObj.carrier_code
            carrierTrackingNo = pickingObj.carrier_tracking_ref
            if not carrierTrackingNo:
                raise UserError(
                    'Warning! Sorry No Carrier Tracking No. Found!!!')
            elif not carrierCode:
                raise UserError('Warning! Please Select Magento Carrier!!!')
            carrierTitle = dict(Carrier_Code)[carrierCode]
            mapObj = self.env['wk.order.mapping'].search(
                [('erp_order_id', '=', saleId)], limit=1)
            if mapObj:
                magOrderId = mapObj.ecommerce_order_id
                ctx['instance_id'] = mapObj.instance_id.id
                shipTrackData = {
                    "entity": {
                        "orderId": magOrderId,
                        "parentId": mageShipment,
                        "trackNumber": carrierTrackingNo,
                        "title": carrierTitle,
                        "carrierCode": carrierCode
                    }
                }
                shipTrackResponse = self.env['magento.synchronization'].with_context(
                    ctx).callMagentoApi(
                    url='/V1/shipment/track',
                    method='post',
                    data=shipTrackData
                )
                if shipTrackResponse:
                    text = 'Tracking number successfully added.'
                else:
                    text = "Error While Syncing Tracking Info At Magento."
                return self.env['magento.synchronization'].display_message(
                    text)
# END

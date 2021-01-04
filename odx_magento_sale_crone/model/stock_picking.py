
from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    is_complete_shipment = fields.Boolean('Complete')

    @api.multi
    def send_to_shipper(self):
        res = super(StockPicking, self).send_to_shipper()
        context = dict(self._context or {})
        orderObj = self.sale_id
        origin = self.origin
        self.is_complete_shipment = True
        if origin == orderObj.name:
            enableOrderShipment = self.env['ir.config_parameter'].sudo().get_param(
                'odoo_magento_connect.mob_sale_order_shipment')
            if orderObj.ecommerce_channel == "magento" and enableOrderShipment:
                itemData = {}
                for moveLine in self.move_line_ids:
                    productSku = moveLine.product_id.default_code or False
                    if productSku :
                        quantity = moveLine.qty_done
                        itemData[productSku] = int(quantity)
                context.update(itemData=itemData)
                mageShipment = orderObj.with_context(context).manual_magento_order_operation(
                    "shipment")
                if mageShipment and mageShipment[0]:
                    self.magento_shipment = mageShipment[0]
                    if self.carrier_tracking_ref:
                        self.action_sync_tracking_no()
        return res
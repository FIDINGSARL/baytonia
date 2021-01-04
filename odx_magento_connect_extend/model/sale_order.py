import logging

import requests
import json
from odoo.exceptions import UserError

from odoo import models, api, fields, _
from odoo.http import request

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    magento_shipment_status = fields.Char("Magento Shipment Status", readonly=1)
    extra_fee = fields.Float("Extra fee")

    @api.constrains('extra_fee')
    def _add_extra_fee_line(self):
        if self.extra_fee > 0:
            extra_fee_product = self.env["product.product"].search([("is_extra_fee", "=", True)], limit=1)
            if extra_fee_product:
                extra_fee_line = self.env['sale.order.line'].create({
                    'product_id': extra_fee_product.id,
                    'name': extra_fee_product.name,
                    'product_uom_qty': 1.0,
                    'product_uom': extra_fee_product.uom_id.id,
                    'order_id': self.id,
                    'tax_id':False,
                    'price_unit': self.extra_fee
                })

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()

        ctx = dict(self._context or {})
        connectionObj = self.env['magento.configure'].search([('active', '=', True)])
        ctx['instance_id'] = connectionObj.id
        connection = self.env['magento.configure'].with_context(ctx)._create_connection()
        for rec in self:
            if connectionObj.active:
                if connectionObj.state != 'enable':
                    return False
            connection = self.env['magento.configure'].with_context(ctx)._create_connection()
            ship_name = ''
            if self.carrier_id:
                ship_name = self.carrier_id.name
            else:
                ship_name = 'Free delivery charges'
            if connection:
                url = connection[0]
                token = connection[1]
                order_mapping_id = self.env["wk.order.mapping"].search([('erp_order_id', '=', rec.id)])
                if order_mapping_id:
                    magento_id = order_mapping_id.ecommerce_order_id
                    path = '/rest/V1/order/{}/invoice'.format(magento_id)
                    api_url = '{}{}'.format(url, path)
                    headers = {'Content-Type': 'application/json',
                               'Authorization': token}
                    data = {
                        "capture": 1,
                        "notify": 0
                    }

                    api_response = requests.post(api_url, data=json.dumps(data), headers=headers)
                    path_sale = '/rest/V1/orders/{}'.format(magento_id)
                    api_url_sale = '{}{}'.format(url, path_sale)
                    userAgent = request.httprequest.environ.get('HTTP_USER_AGENT', '')
                    headers_get = {'Authorization': token,
                                   'Content-Type': 'application/json', 'User-Agent': userAgent}

                    response_get_saleorder = requests.request("GET", url=api_url_sale, headers=headers_get, params='')
                    if response_get_saleorder:
                        sale_order = response_get_saleorder.json()
                        if sale_order:
                            if sale_order['items']:
                                itemslist = []
                                for item in sale_order['items']:
                                    # if item['qty_shipped'] > 0:
                                    #     continue
                                    itemsdict = {'order_item_id': 0, 'qty': 0}
                                    itemsdict['order_item_id'] = item['item_id']
                                    itemsdict['qty'] = item['qty_invoiced']
                                    itemslist.append(itemsdict)

                                    api_url_product = "{}/rest/V1/products/{}".format(url, item['sku'])

                                    response_product = requests.request("GET", url=api_url_product, headers=headers_get,
                                                                        params='')
                                    if response_product:
                                        product_data = response_product.json()
                                        if product_data:
                                            # print(product_data['extension_attributes'])
                                            if product_data['extension_attributes']:
                                                # print(product_data['extension_attributes']['stock_item'])
                                                if product_data['extension_attributes']['stock_item']:
                                                    stocke_item = product_data['extension_attributes']['stock_item']
                                                    if stocke_item['qty'] == 0 and stocke_item[
                                                        'use_config_backorders'] == False:
                                                        stock_item_dict = {
                                                            "qty": item['qty_invoiced']
                                                        }
                                                        data = {
                                                            "stockItem": stock_item_dict
                                                        }
                                                        api_url_product_put = "{}/rest/V1/products/{}/stockItems/{}".format(
                                                            url,
                                                            item['sku'],
                                                            item['store_id'])
                                                        headers_prd_put = {'Accept': '*/*',
                                                                           'Content-Type': 'application/json',
                                                                           'Authorization': token}
                                                        response = requests.request("PUT", url=api_url_product_put,
                                                                                    headers=headers_prd_put,
                                                                                    data=json.dumps(data))
                                path_ship = '/rest/V1/order/{}/ship'.format(magento_id)
                                api_url_ship = '{}{}'.format(url, path_ship)
                                headers_ship = {'Content-Type': 'application/json',
                                                'Authorization': token}
                                data_ship = {
                                    "items": itemslist,
                                    "tracks": [
                                        {
                                            "track_number": self.name,
                                            "title": ship_name,
                                            "carrier_code": "custom"
                                        }
                                    ]

                                }

                                api_response = requests.post(api_url_ship, data=json.dumps(data_ship),
                                                             headers=headers_ship)
                                if api_response:
                                    rec.magento_shipment_status = "Success"
                                else:
                                    rec.magento_shipment_status = "Failed"

        return res

    def action_cancel(self):
        ctx = dict(self._context or {})
        connectionObj = self.env['magento.configure'].search([('active', '=', True)])
        ctx['instance_id'] = connectionObj.id
        for rec in self:
            if connectionObj.active:
                if connectionObj.state != 'enable':
                    return False
            connection = self.env['magento.configure'].with_context(ctx)._create_connection()
            if connection:
                url = connection[0]
                token = connection[1]
                order_mapping_id = self.env["wk.order.mapping"].search([('erp_order_id', '=', rec.id)])
                if order_mapping_id:
                    magento_id = order_mapping_id.ecommerce_order_id
                    if rec.state == 'draft':
                        path = '/rest/V1/orders/{}/cancel'.format(magento_id)
                        api_url = '{}{}'.format(url, path)
                        headers = {'Content-Type': 'application/json',
                                   'Authorization': token}

                        api_response = requests.post(api_url, headers=headers)
        return super(SaleOrder, self).action_cancel()


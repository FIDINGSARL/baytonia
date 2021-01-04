import base64
import json
import logging

import requests

from odoo import models, api, fields
from odoo.http import request

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    def action_invoice_open(self):
        res = super(AccountInvoice, self).action_invoice_open()
        if self.type == 'out_refund':
            invoice = self.search(
                [('number', '=', self.origin)], limit=1)
            if invoice:
                sale_order = self.env['sale.order'].search([('name', '=', invoice.origin)], limit=1)
                # print(sale_order,'sale_order')
                if sale_order:
                    # print('cancelll')
                    ctx = dict(self._context or {})
                    connectionObj = self.env['magento.configure'].search([('active', '=', True)])
                    ctx['instance_id'] = connectionObj.id
                    for rec in sale_order:
                        if connectionObj.active:
                            if connectionObj.state != 'enable':
                                return False
                        connection = self.env['magento.configure'].with_context(ctx)._create_connection()
                        # print(connection, 'coneection')
                        if connection:
                            url = connection[0]
                            token = connection[1]
                            order_mapping_id = self.env["wk.order.mapping"].search([('erp_order_id', '=', rec.id)])
                            if order_mapping_id:
                                magento_id = order_mapping_id.ecommerce_order_id
                                # print('salee')
                                path_sale = '/rest/V1/orders/{}'.format(magento_id)
                                # path_sale = '/rest/V1/orders/14498'
                                api_url_sale = '{}{}'.format(url, path_sale)
                                userAgent = request.httprequest.environ.get('HTTP_USER_AGENT', '')
                                headers_get = {'Authorization': token,
                                               'Content-Type': 'application/json', 'User-Agent': userAgent}

                                response_get_saleorder = requests.request("GET", url=api_url_sale, headers=headers_get,
                                                                          params='')
                                if response_get_saleorder:
                                    sale_order = response_get_saleorder.json()
                                    ship_amount = 0
                                    if sale_order:
                                        ship_amount = sale_order['base_shipping_amount']

                                        if sale_order['items']:
                                            itemslist = []
                                            stock_list = []
                                            for item in sale_order['items']:
                                                itemsdict = {'order_item_id': 0, 'qty': 0}
                                                itemsdict['order_item_id'] = item['item_id']
                                                stock_list.append(item['item_id'])
                                                itemsdict['qty'] = item['qty_invoiced']
                                                itemslist.append(itemsdict)
                                            # print(itemslist, stock_list)

                                            data_ship = {
                                                "items": itemslist,
                                                "notify": 1,
                                                "arguments":
                                                    {
                                                        "shipping_amount": ship_amount,
                                                        "adjustment_positive": 0,
                                                        "adjustment_negative": 0,
                                                        "extension_attributes": {
                                                            "return_to_stock_items": stock_list
                                                        }
                                                    }

                                            }

                                            path = '/rest/V1/order/{}/refund'.format(magento_id)
                                            # path = '/rest/V1/order/14498/refund'
                                            api_url = '{}{}'.format(url, path)
                                            headers = {'Content-Type': 'application/json',
                                                       'Authorization': token}

                                            api_response = requests.post(api_url, data=json.dumps(data_ship),
                                                                         headers=headers)
                                            # print(api_response, 'api_response')
                                            # print(api_response.json(), 'api_responsejson')
                                            amount = self.amount_total
                                            customer_id = sale_order.get('customer_id')

                                            data_credit = {
                                                "customerId": customer_id,
                                                "amount": amount,
                                                "action": 1
                                            }

                                            path_store_credit = '/rest/V1/customer/storecredit'
                                            api_url_store_credit = '{}{}'.format(url, path_store_credit)

                                            response = requests.request("PUT", url=api_url_store_credit, headers=headers,data=json.dumps(data_credit))

        return res

class Accountpayment(models.Model):
    _inherit = "account.payment"

    def action_validate_invoice_payment(self):
        res = super(Accountpayment, self).action_validate_invoice_payment()
        record = self.env['account.invoice'].search([('id', '=', self._context['active_id'])])
        if record:
            if record.type == 'out_refund':
                invoice = self.env['account.invoice'].search(
                    [('number', '=', record.origin)], limit=1)
                if invoice:
                    sale_order = self.env['sale.order'].search([('name', '=', invoice.origin)], limit=1)
                    if sale_order:
                        # print('cancelll')
                        ctx = dict(self._context or {})
                        connectionObj = self.env['magento.configure'].search([('active', '=', True)])
                        ctx['instance_id'] = connectionObj.id
                        for rec in sale_order:
                            if connectionObj.active:
                                if connectionObj.state != 'enable':
                                    return False
                            connection = self.env['magento.configure'].with_context(ctx)._create_connection()
                            # print(connection, 'coneection')
                            if connection:
                                url = connection[0]
                                token = connection[1]
                                order_mapping_id = self.env["wk.order.mapping"].search([('erp_order_id', '=', rec.id)])
                                if order_mapping_id:
                                    magento_id = order_mapping_id.ecommerce_order_id
                                    # print('salee')
                                    path_sale = '/rest/V1/orders/{}'.format(magento_id)
                                    # path_sale = '/rest/V1/orders/14498'
                                    api_url_sale = '{}{}'.format(url, path_sale)
                                    userAgent = request.httprequest.environ.get('HTTP_USER_AGENT', '')
                                    headers_get = {'Authorization': token,
                                                   'Content-Type': 'application/json', 'User-Agent': userAgent}

                                    response_get_saleorder = requests.request("GET", url=api_url_sale,
                                                                              headers=headers_get,
                                                                              params='')
                                    if response_get_saleorder:
                                        sale_order = response_get_saleorder.json()
                                        if sale_order:
                                            headers = {'Content-Type': 'application/json',
                                                       'Authorization': token}

                                            amount = -1 * self.amount
                                            customer_id = sale_order.get('customer_id')

                                            data_credit = {
                                                "customerId": customer_id,
                                                "amount": amount,
                                                "action": 2
                                            }

                                            path_store_credit = '/rest/V1/customer/storecredit'
                                            api_url_store_credit = '{}{}'.format(url, path_store_credit)

                                            response = requests.request("PUT", url=api_url_store_credit,
                                                                        headers=headers,
                                                                            data=json.dumps(data_credit))
        return res

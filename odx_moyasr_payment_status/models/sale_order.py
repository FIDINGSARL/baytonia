import logging
import moyasar
import requests
from odoo import models, fields
from odoo.http import request
from datetime import date, timedelta, datetime

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    moyasar_payment_id = fields.Char("Moyasar Id", readonly=1)

    def moyasar_payment_status(self):
        ctx = dict(self._context or {})
        connectionObj = self.env['magento.configure'].search([('active', '=', True)])
        ctx['instance_id'] = connectionObj.id
        connection = self.env['magento.configure'].with_context(ctx)._create_connection()
        status = "no"
        from_date = str(date.today() - timedelta(days=1))
        date_from = str(from_date) + ' ' + '00:00:00'
        connection = self.env['magento.configure'].with_context(ctx)._create_connection()
        sale_orders = self.search(
            ['|', '|', ('eg_magento_payment_method_id.name', 'ilike', 'دفع عن طريق'),
             ('eg_magento_payment_method_id.name', 'ilike', 'ApplePay'),
             ('eg_magento_payment_method_id.name', 'ilike', 'مدى أو البطاقة الإئتمانية'), ('state', '=', 'draft'),
             ('date_order', '>=', date_from),
             ])
        _logger.info(sale_orders, 'sale_orders')

        for rec in sale_orders:
            if connectionObj.active:
                if connectionObj.state != 'enable':
                    return False
            else:
                text = 'Magento SO update Error For  %s >> Could not able to connect Magento.' % (rec.name)

            connection = self.env['magento.configure'].with_context(ctx)._create_connection()
            if connection:
                url = connection[0]
                token = connection[1]
                order_mapping_id = self.env["wk.order.mapping"].search([('erp_order_id', '=', rec.id)])
                if order_mapping_id:
                    magento_id = order_mapping_id.ecommerce_order_id
                    path = '/rest/V1/orders/{}'.format(magento_id)
                    api_url = '{}{}'.format(url, path)

                    headers = {'Authorization': token,
                               'Content-Type': 'application/json'}
                    try:
                        userAgent = request.httprequest.environ.get('HTTP_USER_AGENT', '')
                        headers.update({'User-Agent': userAgent})
                    except Exception as e:
                        pass

                    # userAgent = request.httprequest.environ.get('HTTP_USER_AGENT', '')
                    # headers = {'Authorization': token,
                    #            'Content-Type': 'application/json', 'User-Agent': userAgent}

                    response = requests.request("GET", url=api_url, headers=headers, params='')
                    if response:
                        data = response.json()
                        if data:
                            if data['payment']:
                                payments = data['payment']['additional_information']
                                _logger.info(
                                    ["===FOUND Sale===", rec.name])
                                _logger.info(
                                    ["===FOUND payments===", payments])
                                if payments:
                                    payment_id = payments[0]
                                    rec.moyasar_payment_id = payments[0]
                                    _logger.info(
                                        ["===FOUND Payment ID===", payment_id])
                                    moyasar.api_key = 'sk_live_NSGfWvU3k8qzbiG2VmrW1KqnXHMpqjdWNPfjjYpA'
                                    # moyasar.api_key = 'sk_test_UPieQaJgKSELrgVKg8WiB1pUSurf6y8BLz9LSAYt'

                                    # moyasar.api_key = 'sk_test_aSoiDtA9ekab3ERNB5bkTiW2USVnT7ZZRYYvJPvM'

                                    try:
                                        payment = moyasar.Payment.fetch(payment_id)

                                        if payment:
                                            if payment.status == 'paid':
                                                rec.action_confirm()
                                    except:
                                        pass

# -*- coding: utf-8 -*-
# Part of odoo. See LICENSE file for full copyright and licensing details.
import logging

import requests

from odoo import api, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class Picking(models.Model):
    _inherit = "stock.picking"

    # @api.model
    # def cron_register_payment(self):
    #     for picking in self:
    #
    #         sale_order_ids = picking.sale_id.search(
    #             [('is_delivered', '=', False), '|', ('payment_gateway_id.code', 'ilike', 'cod'),
    #              ('eg_magento_payment_method_id.code', 'ilike', 'cod')])
    #         for order in sale_order_ids:
    #             if order.invoice_ids.filtered(lambda i: i.state == 'paid'):
    #                 order.is_delivered = True
    #             if not order.is_delivered:
    #                 try:
    #                     picking.vaal_check_delivery_status()
    #                 except Exception as e:
    #                     order.message_post(e)

    @api.multi
    def vaal_check_delivery_status(self):
        for picking in self:
            if picking and picking.carrier_tracking_ref:
                headers = picking.carrier_id.get_vaal_headers()
                url = "https://deliver.vaal.me/ords/vaal/api/v2/orders/status/%s" % (picking.carrier_tracking_ref)
                # url = "https://deliver.vaal.me/ords/vaal/api/v2/orders/status/%s"%('43317270')
                _logger.info(['==========res===', picking.sale_id, '======='])
                _logger.info(['=================', requests.get(url, headers=headers)])
                res = requests.get(url, headers=headers).json()
                _logger.info(['==========res===', res, '======='])
                # {'order_id': 48718510, 'status_ar': 'تم التسليم', 'status_en': 'Delivered'}
                if isinstance(res, dict) and res.get('success') == False:
                    raise ValidationError('%s' % res)
                # if res.get('status_en'):
                #     picking.sale_id.vaal_delivery_status_eg = res.get('status_en')
                if res.get('status_en') == 'Delivered':
                    for inv in picking.sale_id.invoice_ids:
                        if inv.state == 'open':
                            # To Do: journal_id search should be more accurate, fix it
                            journal_id = picking.sale_id.env['account.journal'].search([('code', '=', 'VAAL')], limit=1)
                            if journal_id:
                                is_done = inv.pay_and_reconcile(journal_id.id, pay_amount=inv.residual,
                                                                date=picking.sale_id.date_order,
                                                                writeoff_acc=None)
                                picking.sale_id.is_delivered = is_done
                                break
                else:
                    print(res)
            else:
                return

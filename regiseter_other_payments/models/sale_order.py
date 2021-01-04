# -*- coding: utf-8 -*-
# Part of Futurelens Studio. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def register_payment_paytabs_credit_card(self):
        for inv in self.invoice_ids:
            if inv.state == 'open':
                journal_id = self.env['account.journal'].search([('code', '=', 'BNK5')], limit=1)
                if journal_id:
                    inv.pay_and_reconcile(journal_id.id, pay_amount=inv.residual, date=self.date_order,
                                          writeoff_acc=None)
                    break

    @api.multi
    def register_payment_paytabs_credit_card_action(self):
        count = len(self.ids)
        for order in self:
            # if (order.payment_gateway_id and order.payment_gateway_id.code == 'paytabs') or (
            #         order.eg_magento_payment_method_id and order.eg_magento_payment_method_id.code == 'paytabs'):

            if (order.eg_magento_payment_method_id and order.eg_magento_payment_method_id.code == 'paytabs'):
                # if order.payment_gateway_id and order.payment_gateway_id.code == 'paytabs':
                order.register_payment_paytabs_credit_card()
                count -= 1
                _logger.info(['==========Total PAYTAB===', len(self), '======='])
                _logger.info(['==========Remaining to process===', count, '======='])
            # elif order.eg_magento_payment_method_id and order.eg_magento_payment_method_id.code == 'paytabs':
            #     order.register_payment_paytabs_credit_card()
            #     count -= 1
            #     _logger.info(['==========Total PAYTAB===', len(self), '======='])
            #     _logger.info(['==========Remaining to process===', count, '======='])

    @api.multi
    def register_payment_mada(self):
        for inv in self.invoice_ids:
            if inv.state == 'open':
                journal_id = self.env['account.journal'].search([('code', '=', 'BNK6')], limit=1)
                if journal_id:
                    inv.pay_and_reconcile(journal_id.id, pay_amount=inv.residual, date=self.date_order,
                                          writeoff_acc=None)
                    break

    @api.multi
    def register_payment_mada_action(self):
        count = len(self.ids)
        for order in self:
            # if (order.payment_gateway_id and order.payment_gateway_id.code in ['paytabs-mada', 'paytabs-express']) or (
            #         order.eg_magento_payment_method_id and order.eg_magento_payment_method_id.code in ['paytabs-mada',
            #                                                                                            'paytabs-express']):

            if (order.eg_magento_payment_method_id and order.eg_magento_payment_method_id.code in ['paytabs-mada',
                                                                                                   'paytabs-express']):
                # if order.payment_gateway_id and order.payment_gateway_id.code in ['paytabs-mada', 'paytabs-express']:
                order.register_payment_mada()
                count -= 1
                _logger.info(['==========Total MADA ===', len(self), '======='])
                _logger.info(['==========Remaining to process===', count, '======='])
            # if order.eg_magento_payment_method_id and order.eg_magento_payment_method_id.code in ['paytabs-mada',
            #                                                                                       'paytabs-express']:
            #     order.register_payment_mada()
            #     count -= 1
            #     _logger.info(['==========Total MADA ===', len(self), '======='])
            #     _logger.info(['==========Remaining to process===', count, '======='])

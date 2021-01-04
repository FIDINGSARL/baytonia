# -*- coding: utf-8 -*-
# Part of odoo. See LICENSE file for full copyright and licensing details.
import logging

from odoo import models, api

_logger = logging.getLogger("==Reg smsa payment===")


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def smsa_check_delivery_status(self):
        for picking in self:
            if picking and picking.carrier_tracking_ref:
                if picking.carrier_id.delivery_type == 'smsa':
                    client = picking.carrier_id.get_smsa_client()
                    res = client.service.getStatus(passkey=picking.carrier_id.smsa_pass_key,
                                                   awbNo=picking.carrier_tracking_ref)
                    if res:
                        if res == 'PROOF OF DELIVERY CAPTURED':
                            _logger.info("==Res===SMSA {}".format(res))
                            for inv in picking.sale_id.invoice_ids:
                                if inv.state == 'open':
                                    journal_id = self.env['account.journal'].search([('code', '=', 'SMSA')], limit=1)
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

    # @api.model
    # def cron_register_payment_smsa(self):
    #     sale_order_ids = self.env['sale.order'].search(
    #         [('is_delivered', '=', False), '|', ('payment_gateway_id.code', 'ilike', 'cod'),
    #          ('eg_magento_payment_method_id.code', 'ilike', 'cod')])
    #     count = len(sale_order_ids)
    #     _logger.info("Total {}".format(count))
    #     for order in sale_order_ids:
    #         count -= 1
    #         _logger.info("Remaining {}".format(count))
    #         if order.invoice_ids.filtered(lambda i: i.state == 'paid'):
    #             order.is_delivered = True
    #         if not order.is_delivered:
    #             try:
    #                 order.picking_ids.smsa_check_delivery_status()
    #             except Exception as e:
    #                 order.message_post(e)

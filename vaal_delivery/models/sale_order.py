# -*- coding: utf-8 -*-
# Part of Futurelens Studio. See LICENSE file for full copyright and licensing details.

import logging

import requests

from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # vaal_button_visible = fields.Boolean("VAAL Button Visible", compute='compute_vaal_button', default=False)
    is_delivered = fields.Boolean("Is Delivered ?", readonly=True)

    # vaal_delivery_status_eg = fields.Char("Vaal Delivery states")

    # @api.one
    # @api.depends('order_line')
    # def compute_vaal_button(self):
    #     for rec in self:
    #         if rec.name:
    #             picking = self.env['stock.picking'].search([('sale_id', '=', rec.name),
    #                                                         ('carrier_tracking_ref', '!=', False),
    #                                                         ('state', 'in', ['done']),
    #                                                         # ('carrier_id.delivery_type','=','vaal')
    #                                                         ])
    #             rec.vaal_button_visible = False if picking else True
    #         else:
    #             rec.vaal_button_visible = False

    @api.multi
    def send_to_vaal(self):
        self.ensure_one()
        if self.name is False:
            raise ValidationError('Source Document is not set!')

        # picking = self.env['stock.picking'].search([('sale_id','=',self.name),
        #                                            ('carrier_tracking_ref','=',False),
        #                                            ('state','not in',['cancel'])])
        #
        # Selecting only last created picking/DO
        picking = self.env['stock.picking'].search([('sale_id', '=', self.name),
                                                    ('carrier_tracking_ref', '=', False),
                                                    ('state', 'not in', ['cancel'])], order="id desc", limit=1)

        if len(picking) > 1:
            raise ValidationError(
                'Multiple delivery order found for source document : %s, Please cancel all and create one!' % (
                    self.name))

        elif picking:
            # picking.send_to_kasper_saee()
            carrier_id = self.env['delivery.carrier'].search([('delivery_type', '=', 'vaal')], limit=1)
            picking.carrier_id = carrier_id.id
            # picking.write({'carrier_id':carrier_id.id, 'cod_amount':invoice.residual})
            return picking.with_context(carrier_id='vaal').button_validate()
        else:
            raise ValidationError('No valid delivery order found for source document : %s' % (self.name))
        # else:
        #    raise ValidationError('No open invoice found for sale order : %s'%(self.name))

    @api.multi
    def vaal_check_delivery_status(self):
        self.ensure_one()
        picking = self.env['stock.picking'].search(
            [('sale_id', '=', self.id), ('carrier_tracking_ref', '!=', False),
             ('state', 'in', ['done']),
             ('carrier_id.delivery_type', '=', 'vaal'),
             # '|', ('payment_gateway_id.code', 'ilike', 'cod'),
             ('eg_magento_payment_method_id.code', 'ilike', 'cod')], order="id desc", limit=1)
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
            #     self.vaal_delivery_status_eg = res.get('status_en')
            if res.get('status_en') == 'Delivered':
                for inv in self.invoice_ids:
                    if inv.state == 'open':
                        # To Do: journal_id search should be more accurate, fix it
                        journal_id = self.env['account.journal'].search([('code', '=', 'VAAL')], limit=1)
                        if journal_id:
                            # def pay_and_reconcile(self, pay_journal, pay_amount=None, date=None, writeoff_acc=None)
                            is_done = inv.pay_and_reconcile(journal_id.id, pay_amount=inv.residual,
                                                            date=self.date_order,
                                                            writeoff_acc=None)
                            self.is_delivered = is_done
                            break
            else:
                print(res)
            # raise ValidationError(delivery_status.get(del_status.get('status')))

        # res.raise_for_status()

    # @api.model
    # def cron_register_payment(self):
    #     sale_order_ids = self.search(
    #         [('is_delivered', '=', False), '|', ('payment_gateway_id.code', 'ilike', 'cod'),
    #          ('eg_magento_payment_method_id.code', 'ilike', 'cod')])
    #     for order in sale_order_ids:
    #         if order.invoice_ids.filtered(lambda i: i.state == 'paid'):
    #             order.is_delivered = True
    #         if not order.is_delivered:
    #             try:
    #                 order.vaal_check_delivery_status()
    #             except Exception as e:
    #                 _logger.info("===Error Vaal reg payment ====")
    #                 order.message_post(e)

    @api.multi
    def check_delivery_status_bulk_vaal(self):
        count = len(self.ids)
        for order in self:
            try:
                order.vaal_check_delivery_status()
            except Exception as e:
                order.message_post(e)
            count -= 1
            _logger.info(['==========Total===', len(self), '======='])
            _logger.info(['==========Remaining to process===', count, '======='])

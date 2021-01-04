# -*- coding: utf-8 -*-
# Part of Futurelens Studio. See LICENSE file for full copyright and licensing details.

import logging

import requests

from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # saee_button_visible = fields.Boolean("Saee Button Visible", compute='compute_saee_button', default=False)

    # @api.one
    # @api.depends('order_line', 'invoice_ids')
    # def compute_saee_button(self):
    #     for rec in self:
    #         if rec.name:
    #             picking = self.env['stock.picking'].search(
    #                 [('sale_id', '=', rec.name), ('carrier_tracking_ref', '!=', False),
    #                  ('state', 'in', ['done']),
    #                  # ('carrier_id.delivery_type','=','saee')
    #                  ])
    #             rec.saee_button_visible = False if picking else True
    #         else:
    #             rec.saee_button_visible = False

    @api.multi
    def send_to_kasper_saee(self):
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
            carrier_id = self.env['delivery.carrier'].search([('delivery_type', '=', 'saee')], limit=1)
            picking.carrier_id = carrier_id.id
            # picking.write({'carrier_id':carrier_id.id, 'cod_amount':invoice.residual})
            return picking.with_context(carrier_id='saee').button_validate()
        else:
            raise ValidationError('No valid delivery order found for source document : %s' % (self.name))
        # else:
        #    raise ValidationError('No open invoice found for sale order : %s'%(self.name))

    @api.multi
    def saee_check_delivery_status(self):
        self.ensure_one()
        track_url = "http://www.saee.sa/tracking?trackingnum="
        # http://www.saee.sa/tracking?trackingnum=OS00162955KS
        picking = self.env['stock.picking'].search(
            [('sale_id', '=', self.name), ('carrier_tracking_ref', '!=', False),
             ('state', 'in', ['done']), ('carrier_id.delivery_type', '=', 'saee'), '|',
             # ('payment_gateway_id.code', 'in', ['cod', 'COD']),
             ('eg_magento_payment_method_id.code', 'in', ['cod', 'COD'])], order="id desc", limit=1)
        if picking:
            res = requests.get("%s%s" % (track_url, picking.carrier_tracking_ref)).json()
            if isinstance(res, dict) and res.get('success') == False:
                raise ValidationError('%s' % res)
            delivery_status = {'0': 'Order Created',
                               '1': 'Picked up from supplier',
                               '2': 'Arrived at Kasper warehouse',
                               '3': 'Arrived at Final City',
                               '4': 'Out for Delivery',
                               '5': 'Delivered',
                               '6': 'Failed Delivery Attempt/ Failure Reason',
                               '7': 'Returned to Supplier Warehouse'}

            for del_status in res.get('details'):
                if del_status.get('status') == 5:
                    for inv in self.invoice_ids:
                        if inv.state == 'open':
                            # To Do: journal_id search should be more accurate, fix it
                            journal_id = self.env['account.journal'].search([('code', '=', 'KASPE')], limit=1)
                            if journal_id:
                                # def pay_and_reconcile(self, pay_journal, pay_amount=None, date=None, writeoff_acc=None)
                                inv.pay_and_reconcile(journal_id.id, pay_amount=inv.residual, date=None,
                                                      writeoff_acc=None)
                                break
                else:
                    print(delivery_status.get(str(del_status.get('status'))))
                    # raise ValidationError(delivery_status.get(del_status.get('status')))
            # res.raise_for_status()

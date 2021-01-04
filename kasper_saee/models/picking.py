# -*- coding: utf-8 -*-
# Part of Futurelens Studio. See LICENSE file for full copyright and licensing details.

import logging

import requests

from odoo import api, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class Picking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def saee_check_delivery_status(self):
        self.ensure_one()
        track_url = "http://www.saee.sa/tracking?trackingnum="
        # http://www.saee.sa/tracking?trackingnum=OS00162955KS
        for picking in self:

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
                    for inv in picking.sale_id.invoice_ids:
                        if inv.state == 'open':
                            # To Do: journal_id search should be more accurate, fix it
                            journal_id = self.env['account.journal'].search([('code', '=', 'KASPE')], limit=1)
                            if journal_id:
                                inv.pay_and_reconcile(journal_id.id, pay_amount=inv.residual, date=None,
                                                      writeoff_acc=None)
                                break
                else:
                    print(delivery_status.get(str(del_status.get('status'))))

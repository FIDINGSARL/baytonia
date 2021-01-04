# -*- coding: utf-8 -*-
###################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2017-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: fasluca(<https://www.cybrosys.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange('invoice_ids')
    @api.depends('invoice_ids', 'invoice_status', 'invoice_count', )
    def _payment_status(self):
        """
        Compute the Payment Status invoice associated to the SO.
        """
        for order in self:
            status = 0
            failed = 0
            if order.invoice_ids:
                for item in order.invoice_ids:
                    if item.state not in ('paid', 'cancel'):
                        status = 1
                        break
                    else:
                        order.payment_status = 'paid'
                if status == 1:
                    order.payment_status = 'payment_pending'
            if order.picking_ids:
                for picking in order.picking_ids:
                    if picking.is_return_do:
                        failed = 1
                        break
                if failed == 1:
                    order.payment_status = 'failed'

    payment_status = fields.Selection([
        ('payment_pending', 'Payment Pending'),
        ('paid', 'Paid'), ('failed', 'Failed Payment')], string='Payment Status', store=True, compute='_payment_status',
        track_visibility='always', default='payment_pending')

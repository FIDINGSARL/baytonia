# -*- coding: utf-8 -*-
# Part of Futurelens Studio. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    smsa_button_visible = fields.Boolean("SMSA Button Visible", compute='compute_smsa_button', default=False)

    @api.one
    @api.depends('invoice_line_ids')
    def compute_smsa_button(self):
        for rec in self:
            if rec.origin:
                picking = self.env['stock.picking'].search([('sale_id', '=', rec.origin),
                                                            ('carrier_tracking_ref', '!=', False),
                                                            ('state', 'in', ['done']),
                                                            ])
                rec.smsa_button_visible = False if picking else True
            else:
                rec.smsa_button_visible = False

    @api.multi
    def send_to_smsa(self):
        self.ensure_one()
        if self.origin is False:
            raise ValidationError('Source Document is not set!')
        picking = self.env['stock.picking'].search([('sale_id', '=', self.origin),
                                                    ('carrier_tracking_ref', '=', False),
                                                    ('state', 'not in', ['cancel'])], order="id desc", limit=1)

        if len(picking) > 1:
            raise ValidationError(
                'Multiple delivery order found for sale order : %s, Please cancel all and create one!' % self.origin)

        elif picking:
            carrier_id = self.env['delivery.carrier'].search([('delivery_type', '=', 'smsa')], limit=1)
            if carrier_id:
                self.env.context = dict(self.env.context)
                self.env.context.update({'button': 'true'})
                picking.carrier_id = carrier_id.id
                return picking.send_to_shipper()
        else:
            raise ValidationError('No valid delivery order found for source document : %s' % self.origin)

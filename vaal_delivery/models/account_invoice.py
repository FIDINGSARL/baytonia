# -*- coding: utf-8 -*-
# Part of Futurelens Studio. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)

class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    
    vaal_button_visible = fields.Boolean("VAAL Button Visible", compute='compute_vaal_button',default=False)
    
    @api.one
    @api.depends('invoice_line_ids')
    def compute_vaal_button(self):
        for rec in self:
            if rec.origin:
                picking = self.env['stock.picking'].search([('sale_id','=',rec.origin),
                                                        ('carrier_tracking_ref','!=',False),
                                                        ('state','in',['done']),
                                                        #('carrier_id.delivery_type','=','vaal')
                                                        ])
                rec.vaal_button_visible = False if picking else True
            else:
                rec.vaal_button_visible = False
    
    @api.multi
    def send_to_vaal(self):
        self.ensure_one()
        if self.origin is False:
            raise ValidationError('Source Document is not set!')
        
        #picking = self.env['stock.picking'].search([('sale_id','=',self.origin),
        #                                            ('carrier_tracking_ref','=',False),
        #                                            ('state','not in',['cancel'])])
        #Selecting only last created picking/DO
        picking = self.env['stock.picking'].search([('sale_id','=',self.origin),
                                                    ('carrier_tracking_ref','=',False),
                                                    ('state','not in',['cancel'])], order="id desc", limit=1)
        
        if len(picking) > 1:
            raise ValidationError('Multiple delivery order found for sale order : %s, Please cancel all and create one!'%(self.origin))
        
        elif picking:
            #picking.send_to_kasper_saee()
            carrier_id = self.env['delivery.carrier'].search([('delivery_type','=','vaal')], limit=1)
            picking.carrier_id = carrier_id.id
            #picking.write({'carrier_id':carrier_id.id, 'cod_amount':self.residual})
            return picking.with_context(carrier_id='vaal').button_validate()
        else:
            raise ValidationError('No valid delivery order found for source document : %s'%(self.origin))
        
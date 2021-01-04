# -*- coding: utf-8 -*-
##############################################################################
#
#    Sahil Navadiya
#    Copyright (C) 2018-TODAY (<navadiyasahil@gmail.com>).
#
##############################################################################

from odoo import api, fields, models
from openerp.exceptions import ValidationError

class InfobipSmsHistory(models.Model):
    _name = "fl.infobip.sms.history"
    _description = "Infobip SMS History"
    _order = "id desc"
    _rec_name = "send_to"
    
    send_to = fields.Char()
    send_body = fields.Text("Message")
    state = fields.Selection([('draft','Draft'),('sent','Sent'),('reject','Rejected'),('fail','Failed')], string="State", default="draft")
    api_response = fields.Text("API Response")
    
    
    @api.multi
    def resend_sms(self):
        self.env['fl.infobip.sms'].send_sms(self.send_body, self.send_to, True)
        
    

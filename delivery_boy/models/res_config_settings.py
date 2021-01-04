# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

import logging
_logger = logging.getLogger(__name__)

from odoo import models,fields,api, _

class ResConfigSettings(models.TransientModel):
    _inherit="res.config.settings"

    db_config_id = fields.Many2one(comodel_name='delivery.boy.config')
    db_program_id = fields.Many2one(comodel_name='delivery.boy.programs', string="Program")
    auto_validate = fields.Boolean()
    auto_invoice = fields.Boolean()
    verify_token = fields.Boolean(related="db_config_id.verify_token")
    delivery_token_mail_temp_id = fields.Many2one(comodel_name="mail.template")

    @api.model
    def get_db_configuration(self):
        params = self.env['ir.config_parameter'].sudo()
        config = {
        'program': self.env['delivery.boy.programs'].sudo().browse(int(params.get_param('delivery_boy.db_program_id'))) or False,
        'auto_validate': params.get_param('delivery_boy.auto_validate') or False,
        'auto_invoice': params.get_param('delivery_boy.auto_invoice') or False,
        'verify_token': self.env['delivery.boy.config'].sudo().search([], limit=1).verify_token,
        'delivery_token_mail_temp_id': self.env['mail.template'].sudo().browse(int(params.get_param('delivery_boy.delivery_token_mail_temp_id'))) or False,
        }
        return config

    def set_values(self):
        params = self.env['ir.config_parameter'].sudo()
        super(ResConfigSettings, self).set_values()
        params.set_param('delivery_boy.db_program_id', self.db_program_id.id or False)
        params.set_param('delivery_boy.db_config_id', self.db_config_id.id or False)
        params.set_param('delivery_boy.auto_validate', self.auto_validate or False)
        params.set_param('delivery_boy.auto_invoice', self.auto_invoice or False)
        params.set_param('delivery_boy.delivery_token_mail_temp_id', self.delivery_token_mail_temp_id.id or False)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
        db_program_id = int(params.get_param('delivery_boy.db_program_id')),
        db_config_id = int(params.get_param('delivery_boy.db_config_id')),
        auto_validate = params.get_param('delivery_boy.auto_validate') or False,
        auto_invoice = params.get_param('delivery_boy.auto_invoice') or False,
        delivery_token_mail_temp_id = int(params.get_param('delivery_boy.delivery_token_mail_temp_id'))
        )
        return res

    def open_delivery_boy_conf(self):
        response = {}
        # delivery_boy_config = self.env['delivery.boy.config'].sudo().search([], limit=1)
        params = self.env['ir.config_parameter'].sudo()
        db_config_id = params.get_param('delivery_boy.db_config_id') or False
        if db_config_id:
            response.update({'res_id': int(db_config_id)})

        response.update({
        'type': 'ir.actions.act_window',
        'name': 'Delivery Boy Configuration',
        'view_type': 'form',
        'view_mode': 'form',
        'res_model': 'delivery.boy.config',
        'target': 'current'
        })

        return response

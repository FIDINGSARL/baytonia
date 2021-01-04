# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
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

from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.product'

    expiry_date = fields.Date(string="Product Expiry Date")
    batch_no = fields.Char(string="Product Batch No")

    @api.multi
    def get_product_labels(self):
        return {
            'name':'Download Product Labels',
            'type':'ir.actions.act_window',
            'res_model':'product.label.wizard',
            'view_mode':'form',
            'view_type':'form',
            'view_id':self.env.ref('product_barcode_labels.product_label_wizard_form_view').id,
            'context' : dict(self._context) or {},
            'target':'new',
        }

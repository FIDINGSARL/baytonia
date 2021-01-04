# -*- coding: utf-8 -*-
##########################################################################
# 2010-2017 Webkul.
#
# NOTICE OF LICENSE
#
# All right is reserved,
# Please go through this link for complete license : https://store.webkul.com/license.html
#
# DISCLAIMER
#
# Do not edit or add to this file if you wish to upgrade this module to newer
# versions in the future. If you wish to customize this module for your
# needs please refer to https://store.webkul.com/customisation-guidelines/ for more information.
#
# @Author        : Webkul Software Pvt. Ltd. (<support@webkul.com>)
# @Copyright (c) : 2010-2017 Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# @License       : https://store.webkul.com/license.html
#
##########################################################################
import logging
_logger = logging.getLogger(__name__)

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ProductLabelWizard(models.TransientModel):
    _name="product.label.wizard"


    @api.model
    def default_get(self,default_fields):
        res = super(ProductLabelWizard,self).default_get(default_fields)
        if self._context.get('preview',False):
            res['preview'] = True
            res['l_config'] = self._context.get('l_config')
        return res


    l_config = fields.Many2one("label.configurator")
    product_ids = fields.Many2many("product.product")
    product_id = fields.Many2one("product.product")
    preview = fields.Boolean()

    @api.multi
    def download_product_labels(self):
        context = dict(self._context) or {}
        if context.get('active_model',False) and context.get('active_model') == 'product.product' and context.get('active_ids',False):
            self.product_ids = [(6,0,context.get('active_ids'))]

        self.ensure_one()
        list1 = []

        if self.preview:
            if not self.product_id:
                raise UserError(_("Please select a product first."))
            else:
                self.product_ids = [(6,0,[self.product_id.id])]
        elif not self.l_config:
            raise UserError(_("Please select type of label first."))

        if self.l_config.barcode_field == 'hs_code':
            for product in self.product_ids:
                if not product.hs_code:
                    list1.append(product.name)
        else:
            for product in self.product_ids:
                if not product.barcode:
                    list1.append(product.name)

        if len(list1) != 0:
            b_field = "HS Code" if self.l_config.barcode_field == 'hs_code' else "Barcode"
            msg = "Sorry, " + b_field + " is missing in the below listed product(s). In order to generate labels please fill "+ b_field +" for all.\n\nProducts:\n["+ ', '.join(list1) + "]"
            raise UserError(_(msg))

        return {
            'type' : 'ir.actions.act_url',
            'url': '/product/binary/download_labels?model=product.label.wizard&id=%s' % (self.id),
            'target': 'self',
        }

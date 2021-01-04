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
from odoo import models,fields,api,_
from openerp.exceptions import Warning, UserError

import logging
_logger = logging.getLogger(__name__)

B_TYPE = [('Codabar','CODABAR'),('Code11','CODE 11'),('Code128','CODE 128'),('EAN13','EAN-13'),
            ('EAN8','EAN-8'),('Extended39','EXTENDED 39'),('Extended93','EXTENDED 93'),('I2of5','INTERLEAVED 2 OF 5'),
            ('MSI','MSI'),('Standard39','STANDARD 39'),('Standard93','STANDARD 93'),('UPCA','UPC-A'),]

class LabelConfigurator(models.Model):
    _name = "label.configurator"

    name = fields.Char("PDF Name", help="Enter product PDF name")
    orientation = fields.Selection([('Landscape', 'Landscape'), ('Portrait', 'Portrait')], "Orientation", help="Select product label page orientation")
    barcode_field = fields.Selection(selection=[('hs_code','HS Code'),('barcode','Barcode')], string="Barcode Field", default="barcode", help="Select a barcode field from HS Code/Barcode.")
    barcode_type = fields.Selection(selection=B_TYPE, string="Barcode Type", default="Code128", help="Select barcode standards: EAN 13, UPC, Code 128, code 39 ...")
    label_layout_ids = fields.One2many("label.layout.lines", "label_config_id", string="Label Layout")

    @api.multi
    def get_product_labels_preview(self):
        self.ensure_one()
        context = dict(self._context) or {}
        context['l_config'] = self.id
        context['preview'] = True
        return {
            'name':'Download Product Labels',
            'type':'ir.actions.act_window',
            'res_model':'product.label.wizard',
            'view_mode':'form',
            'view_type':'form',
            'view_id':self.env.ref('product_barcode_labels.product_label_wizard_form_view').id,
            'context' : context,
            'target':'new',
        }


class LabelLayoutLines(models.Model):
    _name = "label.layout.lines"

    name = fields.Char("Layout Name", help="Enter product label name")
    label_config_id = fields.Many2one("label.configurator", string="Label Configurator")
    orientation = fields.Selection([('Landscape', 'Landscape'), ('Portrait', 'Portrait')], "Orientation", related="label_config_id.orientation")
    pdf_type = fields.Selection([('small', 'Small'), ('medium', 'Medium'), ('large', 'Large')], "Label Size",)
    width = fields.Integer("Width", help="Width of generated product label")
    height = fields.Integer("Height", help="Height of generated product label")
    image = fields.Boolean("Image", help="Enable this to show product image in label")
    description_sale = fields.Boolean("Sale Description", help="Enable this to show product sale description in label")
    description_pick = fields.Boolean("Picking Description", help="Enable this to show product picking description in label")
    weight = fields.Boolean("Weight", help="Enable this to show product weight in label", default=True)
    expiry_date = fields.Boolean("Expiry Date", help="Enable this to show product expiry date in label", default=True)
    batch_no = fields.Boolean("Batch No", help="Enable this to show product batch no in label", default=True)
    default_code = fields.Boolean("Internal Reference", help="Enable this to show product internal reference in label", default=True)
    attributes = fields.Boolean("Attributes", help="Enable this to show product attributes in label", default=True)
    price = fields.Boolean("Price", help="Enable this to show product price in label", default=True)
    pricelist_id = fields.Many2one('product.pricelist', 'Pricelist')
    currency = fields.Boolean("Currency", help="Enable this to show currency in label", default=True)
    human_readable = fields.Boolean("Human Readable Barcode", help="Enable this if you want barcode is human readable", default=True)

    @api.model
    def validate_width_and_height_of_template(self, width, height, pdf_type, orientation):
        if orientation == 'Landscape':
            if pdf_type == 'small' and (width > 550 or width < 450 or height > 100 or height < 50):
                return False
            if pdf_type == 'medium' and (width > 900 or width < 800 or height > 100 or height < 50):
                return False
            if pdf_type == 'large' and (width > 1100 or width < 900 or height > 300 or height < 200):
                return False

        elif orientation == 'Portrait':
            if pdf_type == 'small' and (width > 400 or width < 300 or height > 200 or height < 100):
                return False
            if pdf_type == 'medium' and (width > 500 or width < 400 or height > 700 or height < 600):
                return False
            if pdf_type == 'large' and (width > 800 or width < 700 or height > 900 or height < 700):
                return False
        return True

    @api.model
    def create(self, vals):
        label_config_id = vals.get('label_config_id')
        config_obj = self.env["label.configurator"].browse(label_config_id)
        result = self.validate_width_and_height_of_template(vals.get('width'), vals.get('height'), vals.get('pdf_type'), config_obj.orientation)
        if not result:
            raise UserError(_("Size of '"+ vals.get('name') +"' label layout is not valid, Please update it."))
        res = super(LabelLayoutLines,self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        name = vals.get('name') if vals.get('name',False) else self.name
        width = vals.get('width') if vals.get('width',False) else self.width
        height = vals.get('height') if vals.get('height',False) else self.height
        pdf_type = vals.get('pdf_type') if vals.get('pdf_type',False) else self.pdf_type
        orientation = vals.get('orientation') if vals.get('orientation',False) else self.orientation
        result = self.validate_width_and_height_of_template(width, height, pdf_type, orientation)
        if not result:
            raise UserError(_("Size of '"+ name +"' label layout is not valid, Please update it."))
        res = super(LabelLayoutLines,self).write(vals)
        return res

    @api.onchange('pdf_type')
    def set_attribute_of_template(self):
        self.image = True
        self.description_sale = True
        self.description_pick = True
        if self.pdf_type == 'small':
            self.image = False
            self.description_sale = False
            self.description_pick = False
        elif self.pdf_type == 'medium':
            self.image = False


    @api.onchange('width')
    def validate_width_of_template(self):
        if self.label_config_id.orientation and self.pdf_type:
            if self.label_config_id.orientation == 'Landscape':
                if self.pdf_type == 'small' and (self.width > 550 or self.width < 450):
                    raise UserError(_("Please enter width correctly. For landscape-small size pdf width x height will be in range (450-550)x(50-100)."))
                if self.pdf_type == 'medium' and (self.width > 900 or self.width < 800):
                    raise UserError(_("Please enter width correctly. For landscape-medium size pdf width x height will be in range (800-900)x(50-100)."))
                if self.pdf_type == 'large' and (self.width > 1100 or self.width < 900):
                    raise UserError(_("Please enter width correctly. For landscape-large size pdf width x height will be in range (900-1100)x(200-300)."))

            elif self.label_config_id.orientation == 'Portrait':
                if self.pdf_type == 'small' and (self.width > 400 or self.width < 300):
                    raise UserError(_("Please enter width correctly. For portrait-small size pdf width x height will be in range (300-400)x(100-200)."))
                if self.pdf_type == 'medium' and (self.width > 500 or self.width < 400):
                    raise UserError(_("Please enter width correctly. For portrait-medium size pdf width x height will be in range (400-500)x(600-700)."))
                if self.pdf_type == 'large' and (self.width > 800 or self.width < 700):
                    raise UserError(_("Please enter width correctly. For portrait-large size pdf width x height will be in range (700-800)x(700-900)."))

    @api.onchange('height')
    def validate_height_of_template(self):
        if self.label_config_id.orientation and self.pdf_type:
            if self.label_config_id.orientation == 'Landscape':
                if self.pdf_type == 'small' and (self.height > 100 or self.height < 50):
                        raise UserError(_("Please enter height correctly. For landscape-small size pdf width x height will be in range (450-550)x(50-100)."))
                if self.pdf_type == 'medium' and (self.height > 100 or self.height < 50):
                        raise UserError(_("Please enter height correctly. For landscape-medium size pdf width x height will be in range (800-900)x(50-100)."))
                if self.pdf_type == 'large' and (self.height > 300 or self.height < 200):
                        raise UserError(_("Please enter height correctly. For landscape-large size pdf width x height will be in range (900-1100)x(200-300)."))

            elif self.label_config_id.orientation == 'Portrait':
                if self.pdf_type == 'small' and (self.height > 200 or self.height < 100):
                    raise UserError(_("Please enter height correctly. For portrait-small size pdf width x height will be in range (300-400)x(100-200)."))
                if self.pdf_type == 'medium' and (self.height > 700 or self.height < 600):
                    raise UserError(_("Please enter height correctly. For portrait-medium size pdf width x height will be in range (400-500)x(600-700)."))
                if self.pdf_type == 'large' and (self.height > 900 or self.height < 700):
                    raise UserError(_("Please enter height correctly. For portrait-large size pdf width x height will be in range (700-800)x(700-900)."))

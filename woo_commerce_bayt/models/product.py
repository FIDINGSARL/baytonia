# -*- coding: utf-8 -*-

from odoo import models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    def woo_published(self):
        woo_product_template_obj = self.env['woo.product.template.ept']
        for template in self:
            unpublished_woo_templates = woo_product_template_obj.search(
                [('product_tmpl_id', '=', template.id), ('website_published', '=', False)])
            unpublished_woo_templates.woo_published()

    @api.multi
    def woo_unpublished(self):
        woo_product_template_obj = self.env['woo.product.template.ept']
        for template in self:
            published_woo_templates = woo_product_template_obj.search(
                [('product_tmpl_id', '=', template.id), ('website_published', '=', True)])
            published_woo_templates.woo_unpublished()

    # @api.multi
    # def write(self, vals):
    #     res = super(ProductTemplate, self).write(vals)
    #     if res and 'active' in vals:
    #         if vals['active']:
    #             self.woo_published()
    #         else:
    #             self.woo_unpublished()
    #     return res

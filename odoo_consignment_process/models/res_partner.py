# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    po_consignment_product_count = fields.Integer(
        string="Consignment Product Count",
        compute="_po_consignment_product_count",
    )
    so_consignment_product_count = fields.Integer(
        string="Consignment Product Count",
        compute="_so_consignment_product_count",
    )

    @api.depends()
    def _so_consignment_product_count(self):
        pro_ids = []
        for rec in self:
            product_ids = self.env['product.product'].search([('sale_order_line_ids', '!=', False)])
            for product in product_ids:
                for line in product.sale_order_line_ids:
                    if line.order_id.partner_id == rec:
                        if not product.id in pro_ids:
                            pro_ids.append(product.id)
            rec.so_consignment_product_count = len(pro_ids)
#             rec.so_consignment_product_count = self.env['product.product'].search_count([
#                 ('sale_order_line_id.order_id.partner_id', '=', rec.id),
#                 ('sale_order_line_id.order_id.is_consignment', '=', True)
#             ])

    @api.depends()
    def _po_consignment_product_count(self):
        for rec in self:
            rec.po_consignment_product_count = self.env['product.product'].search_count([
                ('purchase_order_line_id.order_id.partner_id', '=', rec.id),
                ('purchase_order_line_id.order_id.is_consignment', '=', True)
            ])

    @api.multi
    def show_po_consignment_product(self):
        for rec in self:
            res = self.env.ref('product.product_normal_action_sell')
            res = res.read()[0]
            res['domain'] = str([
                ('purchase_order_line_id.order_id.partner_id', '=', rec.id),
                ('purchase_order_line_id.order_id.is_consignment', '=', True)
            ])
        return res

    @api.multi
    def show_so_consignment_product(self):
        pro_ids = []
        for rec in self:
            res = self.env.ref('product.product_normal_action_sell')
            res = res.read()[0]
            product_ids = self.env['product.product'].search([('sale_order_line_ids', '!=', False)])
            for product in product_ids:
                for line in product.sale_order_line_ids:
                    if line.order_id.partner_id == rec:
                        pro_ids.append(product.id)
            res['domain'] = str([
                ('id', 'in', pro_ids),
            ])
        return res

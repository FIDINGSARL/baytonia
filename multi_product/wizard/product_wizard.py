# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductWizard(models.TransientModel):

    _name = 'product.wizard'

    product_ids = fields.Many2many('product.product', string='Products')

    @api.multi
    def add_products(self):
        if self._context.get('active_model') == 'sale.order':
            order_line_obj = self.env['sale.order.line']
            for product in self.product_ids:
                order_line = order_line_obj.create({
                    'product_id': product.id,
                    'order_id': self._context.get('active_id', False),
                })
                order_line.product_id_change()
        elif self._context.get('active_model') == 'purchase.order':
            po_line_obj = self.env['purchase.order.line']
            order_id = self.env['purchase.order'].browse(self._context.get('active_id'))
            for product in self.product_ids:
                po_line = po_line_obj.create({
                    'product_id': product.id,
                    'order_id': self._context.get('active_id', False),
                    'name': product.name,
                    'product_qty': 1.0,
                    'date_planned': order_id.date_planned,
                    'product_uom': product.uom_id.id,
                    'price_unit': product.lst_price,
                })
                po_line.onchange_product_id()
        elif self._context.get('active_model') == 'stock.picking':
            picking = self.env['stock.picking'].browse(
                self._context.get('active_id',False))
            location_src_id = picking.location_id.id or picking.picking_type_id.default_location_src_id.id
            location_dest_id = picking.location_dest_id.id or picking.picking_type_id.default_location_src_id.id
            if picking.picking_type_code == 'incoming':
                location_src_id = self.env.ref(
                    'stock.stock_location_suppliers').id
                # location_dest_id = self.env.ref(
                #     'stock.stock_location_stock').id
            elif picking.picking_type_code == 'outgoing':
                # location_src_id = self.env.ref(
                #     'stock.stock_location_stock').id
                location_dest_id = self.env.ref(
                    'stock.stock_location_customers').id
            for product in self.product_ids:
                move_line = self.env['stock.move'].create({
                    'product_id': product.id,
                    'picking_id': self._context.get('active_id', False),
                    'name': product.name,
                    'product_uom': product.uom_id.id,
                    'location_id': location_src_id,
                    'location_dest_id': location_dest_id,
                })
                move_line.onchange_product_id()

        elif self._context.get('active_model') == 'account.invoice':
            invoice_obj = self.env['account.invoice']
            invoice_line_obj = self.env['account.invoice.line']
            invoice = invoice_obj.browse(
                self._context.get('active_id', False))
            part = invoice.partner_id
            fpos = invoice.fiscal_position_id
            company = invoice.company_id
            currency = invoice.currency_id
            type = invoice.type

            for product in self.product_ids:
                account = invoice_line_obj.get_invoice_line_account(type, product, fpos,
                                                        company)
                invoice_line = invoice_line_obj.create({
                    'product_id': product.id,
                    'invoice_id': self._context.get('active_id', False),
                    'price_unit': product.lst_price,
                    'name': product.name,
                    'quantity': 1.0,
                    'account_id': account.id
                })
                invoice_line._onchange_product_id()
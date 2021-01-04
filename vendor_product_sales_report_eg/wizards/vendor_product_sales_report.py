import base64
import io
import logging
from calendar import monthrange
from datetime import datetime, date, timedelta

import xlwt
from xlwt import easyxf

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)


class VendorProductSalesReport(models.TransientModel):
    _name = "vendor.product.sales.report.eg"

    @api.model
    def _default_from_date(self):
        return date.today() - timedelta(days=7)

    vendor_ids = fields.Many2many("res.partner", string="Vendors")
    vendor_sales_report_file = fields.Binary('Invoice Report')
    vendor_sales_report_printed = fields.Boolean('Invoice Report Printed')
    file_name = fields.Char('File Name')
    to_date = fields.Date(string="To Date", default=date.today())
    from_date = fields.Date(string="From Date", default=_default_from_date)
    master_report = fields.Boolean("Master Report?")
    partner_category_ids = fields.Many2many("res.partner.category", string="Tags")

    @api.multi
    def action_vendor_sales_report_line_eg(self):
        vendor_product_line = self.env['vendor.product.sales.line']
        vendor_product_line.search([]).unlink()
        for wizard in self:
            if wizard.partner_category_ids:
                vendor_ids = []
                for vendor in wizard.vendor_ids:
                    if vendor.category_id in wizard.partner_category_ids:
                        vendor_ids.append(vendor)
            else:
                vendor_ids = wizard.vendor_ids
            for vendor_id in vendor_ids:
                supplierifo_ids = self.env['product.supplierinfo'].search([('name', '=', vendor_id.id)])
                product_tmpl_ids = supplierifo_ids.mapped('product_tmpl_id')
                product_ids = product_tmpl_ids.mapped('product_variant_ids')
                _logger.info(["=====PRODUCT=>", product_ids, "====LEN===", len(product_ids)])
                product_counter = len(product_ids)
                _logger.info(["=====Total Len=>", product_counter])
                for product_id in product_ids:
                    move_ids = self.env['stock.move'].search([('date', '>=', self.from_date),
                                                              ('date', '<=', self.to_date),
                                                              ('state', '=', 'done'),
                                                              ('product_id', '=', product_id.id),
                                                              ('sale_line_id', '!=', False)])
                    _logger.info(["=====Product=>", product_id.display_name])

                    for move_id in move_ids:
                        line_dict = {}
                        sale_line_id = move_id.sale_line_id
                        total_sold_qty = sale_line_id.qty_delivered
                        sale_price = sale_line_id.price_unit
                        profit = (sale_price - product_id.standard_price) * total_sold_qty
                        cost = product_id.standard_price * total_sold_qty
                        if self.master_report:
                            line_dict.update({'sale_price': sale_price})
                            line_dict.update({'profit': profit})
                        line_dict.update({
                            'sale_order_id': sale_line_id.order_id.id,
                            'picking_id': sale_line_id.move_ids[0].picking_id.id,
                            'product_id': product_id.id,
                            'image_small': product_id.image_small,
                            'cost_price': product_id.standard_price,
                            'total_sold': total_sold_qty,
                            'total_cost': cost,
                            'vendor_id': vendor_id.id,
                            'from_date': self.from_date,
                            'to_date': self.to_date,
                        })
                        self.env['vendor.product.sales.line'].create(line_dict)

                        refund_ids = sale_line_id.order_id.invoice_ids.filtered(lambda i: i.type == 'out_refund')
                        for refund_id in refund_ids:
                            refund_line_dict = {}
                            refund_product_lines = refund_id.invoice_line_ids.filtered(
                                lambda l: l.product_id.id == product_id.id)
                            for refund_product_line in refund_product_lines:
                                if refund_product_line:
                                    total_returned_qty = refund_product_line.quantity
                                    refund_price = refund_product_line.price_unit
                                    loss_of_profit = (refund_price - product_id.standard_price) * total_returned_qty
                                    cost_to_deduct = product_id.standard_price * total_returned_qty
                                    if self.master_report:
                                        refund_line_dict.update({'sale_price': refund_price})
                                        refund_line_dict.update({'profit': -loss_of_profit})

                                    refund_line_dict.update({
                                        'sale_order_id': sale_line_id.order_id.id,
                                        'is_return': True,
                                        'product_id': product_id.id,
                                        'image_small': product_id.image_small,
                                        'cost_price': product_id.standard_price,
                                        'total_sold': -total_returned_qty,
                                        'total_cost': -cost_to_deduct,
                                        'vendor_id': vendor_id.id,
                                        'from_date': self.from_date,
                                        'to_date': self.to_date,
                                    })

                                    self.env['vendor.product.sales.line'].create(refund_line_dict)

                    if self.master_report:
                        # Purchase Data
                        purchase_line_ids = self.env['purchase.order.line'].search([
                            ('date_planned', '>=', self.from_date),
                            ('date_planned', '<=', self.to_date),
                            ('state', 'in', ['done', 'purchase']),
                            ('product_id', '=', product_id.id)])
                        for purchase_line_id in purchase_line_ids:
                            purchase_line_dict = {}
                            total_purchased_qty = purchase_line_id.qty_received
                            purchase_price = purchase_line_id.price_unit
                            cost = purchase_line_id.price_unit * total_purchased_qty
                            if self.master_report:
                                purchase_line_dict.update({'sale_price': purchase_price})

                            purchase_line_dict.update({
                                'sale_order_id': purchase_line_id.order_id.id,
                                'picking_id': purchase_line_id.move_ids[0].picking_id.id,
                                'product_id': product_id.id,
                                'image_small': product_id.image_small,
                                'cost_price': product_id.standard_price,
                                'total_sold': total_purchased_qty,
                                'total_cost': cost,
                                'vendor_id': vendor_id.id,
                                'from_date': self.from_date,
                                'to_date': self.to_date,
                            })
                            self.env['vendor.product.sales.line'].create(purchase_line_dict)

        action = self.env.ref('vendor_product_sales_report_eg.action_vendor_product_line').read()[0]
        return action

    @api.multi
    def action_vendor_sales_report_eg(self):
        workbook = xlwt.Workbook()
        column_heading_style = easyxf(
            'font:height 200;font:bold True;' "borders: top thin, bottom thin, left thin, right thin;")
        column_footer_style = easyxf(
            'font:height 200;font:bold True;')
        column_normal_style = easyxf(
            'font:height 200;' "borders: top thin, bottom thin, left thin,    right thin;")
        column_return_style = easyxf(
            'font:height 200;' "borders: top thin, bottom thin, left thin, right thin;pattern: pattern solid, fore_color red;")
        column_purchase_style = easyxf(
            'font:height 200;' "borders: top thin, bottom thin, left thin, right thin;pattern: pattern solid, fore_color yellow;")
        vendor_names = ", ".join(self.vendor_ids.mapped("name"))
        worksheet = workbook.add_sheet("Vendor: {} Sales Report".format(vendor_names))
        worksheet.write(2, 2, self.env.user.company_id.name,
                        easyxf('font:height 200;font:bold True;align: horiz center;'))
        worksheet.write(4, 1, self.from_date, easyxf('font:height 200;font:bold True;align: horiz center;'))
        worksheet.write(4, 2, 'To', easyxf('font:height 200;font:bold True;align: horiz center;'))
        worksheet.write(4, 3, self.to_date, easyxf('font:height 200;font:bold True;align: horiz center;'))
        hearder_counter = 0
        worksheet.write(6, hearder_counter, 'Sale Order', column_heading_style)
        hearder_counter += 1
        worksheet.write(6, hearder_counter, 'Delivery Oder', column_heading_style)
        hearder_counter += 1
        worksheet.write(6, hearder_counter, 'Product Name', column_heading_style)
        hearder_counter += 1
        worksheet.write(6, hearder_counter, 'Cost Price', column_heading_style)
        hearder_counter += 1
        if self.master_report:
            worksheet.write(6, hearder_counter, 'Selling Price', column_heading_style)
            hearder_counter += 1
        worksheet.write(6, hearder_counter, 'Total Sold', column_heading_style)
        hearder_counter += 1
        worksheet.write(6, hearder_counter, 'Total Cost', column_heading_style)
        hearder_counter += 1
        if self.master_report:
            worksheet.write(6, hearder_counter, 'Profit', column_heading_style)
            hearder_counter += 1

        worksheet.col(0).width = 5000
        worksheet.col(1).width = 5000
        worksheet.col(2).width = 5000
        worksheet.col(3).width = 5000
        worksheet.col(4).width = 5000
        worksheet.col(5).width = 5000

        row = 7
        for wizard in self:
            if wizard.partner_category_ids:
                vendor_ids = []
                for vendor in wizard.vendor_ids:
                    if vendor.category_id in wizard.partner_category_ids:
                        vendor_ids.append(vendor)
            else:
                vendor_ids = wizard.vendor_ids
            for vendor_id in vendor_ids:
                heading = "Vendor: {} Sales Report".format(vendor_id.name)
                worksheet.write_merge(row, row, 0, 6, heading, easyxf(
                    'font:height 210; align: horiz center;pattern: pattern solid,'
                    ' fore_color black; font: color white; font:bold True;' "borders: top thin,bottom thin"))
                row += 1
                supplierifo_ids = self.env['product.supplierinfo'].search([('name', '=', vendor_id.id)])
                product_tmpl_ids = supplierifo_ids.mapped('product_tmpl_id')
                product_ids = product_tmpl_ids.mapped('product_variant_ids')
                total_profit = 0
                total_sales_cost = 0
                total_purchase_cost = 0
                _logger.info(["=====PRODUCT=>", product_ids, "====LEN===", len(product_ids)])
                product_counter = len(product_ids)
                _logger.info(["=====Total Len=>", product_counter])
                for product_id in product_ids:
                    # ====================== Sales Data
                    # sale_line_ids = self.env['sale.order.line'].search([
                    #     ('order_id.date_order', '>=', self.from_date),
                    #     ('order_id.date_order', '<=', self.to_date),
                    #     ('state', 'in', ['done', 'sale']),
                    #     ('product_id', '=', product_id.id)])
                    # Old Logic
                    move_ids = self.env['stock.move'].search([('date', '>=', self.from_date),
                                                              ('date', '<=', self.to_date),
                                                              ('state', '=', 'done'),
                                                              ('product_id', '=', product_id.id),
                                                              ('sale_line_id', '!=', False)])
                    # product_move_ids = move_ids.filtered(
                    #     lambda m: m.picking_id.sale_id and m.picking_code == "outgoing")
                    # _logger.info(["=====MOVE=>", product_id])
                    # _logger.info(["=====MOVE=>", product_move_ids])
                    # for product_move_id in product_move_ids:
                    #     sale_price = 0
                    #     total_sold_qty = product_move_id.quantity_done
                    #     sale_line_ids = product_move_id.picking_id.sale_id.order_line.filtered(
                    #         lambda l: l.product_id.id == product_id.id)
                    _logger.info(["=====Product=>", product_id.display_name])
                    for move_id in move_ids:
                        sale_line_id = move_id.sale_line_id
                        total_sold_qty = sale_line_id.qty_delivered
                        sale_price = sale_line_id.price_unit
                        profit = (sale_price - product_id.standard_price) * total_sold_qty
                        cost = product_id.standard_price * total_sold_qty
                        column_counter = 0
                        worksheet.write(row, column_counter, sale_line_id.order_id.name, column_normal_style)
                        column_counter += 1
                        worksheet.write(row, column_counter, sale_line_id.move_ids.mapped('picking_id').mapped('name'),
                                        column_normal_style)
                        column_counter += 1
                        worksheet.write(row, column_counter, product_id.display_name, column_normal_style)
                        column_counter += 1
                        worksheet.write(row, column_counter, product_id.standard_price, column_normal_style)
                        column_counter += 1
                        if self.master_report:
                            worksheet.write(row, column_counter, sale_price, column_normal_style)
                            column_counter += 1
                        worksheet.write(row, column_counter, total_sold_qty, column_normal_style)
                        column_counter += 1
                        worksheet.write(row, column_counter, cost, column_normal_style)
                        column_counter += 1
                        if self.master_report:
                            worksheet.write(row, column_counter, profit, column_normal_style)
                        row += 1
                        total_profit += profit
                        total_sales_cost += cost

                        refund_ids = sale_line_id.order_id.invoice_ids.filtered(lambda i: i.type == 'out_refund')
                        for refund_id in refund_ids:
                            refund_product_lines = refund_id.invoice_line_ids.filtered(
                                lambda l: l.product_id.id == product_id.id)
                            for refund_product_line in refund_product_lines:
                                if refund_product_line:
                                    total_returned_qty = refund_product_line.quantity
                                    refund_price = refund_product_line.price_unit
                                    loss_of_profit = (refund_price - product_id.standard_price) * total_returned_qty
                                    cost_to_deduct = product_id.standard_price * total_returned_qty
                                    column_counter = 0
                                    worksheet.write(row, column_counter, sale_line_id.order_id.name,
                                                    column_return_style)
                                    column_counter += 1
                                    worksheet.write(row, column_counter, "Returned", column_return_style)
                                    column_counter += 1
                                    worksheet.write(row, column_counter, product_id.display_name,
                                                    column_return_style)
                                    column_counter += 1
                                    worksheet.write(row, column_counter, product_id.standard_price,
                                                    column_return_style)
                                    column_counter += 1
                                    if self.master_report:
                                        worksheet.write(row, column_counter, refund_price, column_return_style)
                                        column_counter += 1
                                    worksheet.write(row, column_counter, -total_returned_qty, column_return_style)
                                    column_counter += 1
                                    worksheet.write(row, column_counter, -cost_to_deduct, column_return_style)
                                    column_counter += 1
                                    if self.master_report:
                                        worksheet.write(row, column_counter, -loss_of_profit, column_return_style)
                                    row += 1
                                    total_profit -= loss_of_profit
                                    total_sales_cost -= cost_to_deduct
                    if self.master_report:
                        # Purchase Data
                        purchase_line_ids = self.env['purchase.order.line'].search([
                            ('date_planned', '>=', self.from_date),
                            ('date_planned', '<=', self.to_date),
                            ('state', 'in', ['done', 'purchase']),
                            ('product_id', '=', product_id.id)])
                        for purchase_line_id in purchase_line_ids:
                            total_purchased_qty = purchase_line_id.qty_received
                            purchase_price = purchase_line_id.price_unit
                            cost = purchase_line_id.price_unit * total_purchased_qty
                            column_counter = 0
                            worksheet.write(row, column_counter, purchase_line_id.order_id.name,
                                            column_purchase_style)
                            column_counter += 1
                            worksheet.write(row, column_counter,
                                            purchase_line_id.move_ids.mapped('picking_id').mapped('name'),
                                            column_purchase_style)
                            column_counter += 1
                            worksheet.write(row, column_counter, product_id.display_name, column_purchase_style)
                            column_counter += 1
                            worksheet.write(row, column_counter, product_id.standard_price, column_purchase_style)
                            column_counter += 1
                            if self.master_report:
                                worksheet.write(row, column_counter, purchase_price, column_purchase_style)
                                column_counter += 1
                            worksheet.write(row, column_counter, total_purchased_qty, column_purchase_style)
                            column_counter += 1
                            worksheet.write(row, column_counter, cost, column_purchase_style)
                            row += 1
                            total_purchase_cost += cost
                    _logger.info(["=====Remaining=>", product_counter])
                    product_counter -= 1
                if self.master_report:
                    worksheet.write(row, 6, "Total Profit", column_footer_style)
                    worksheet.write(row, 7, total_profit, column_footer_style)
                    row += 1
                    worksheet.write(row, 6, "Total Sales Cost", column_footer_style)
                    worksheet.write(row, 7, total_sales_cost, column_footer_style)
                    row += 1
                    worksheet.write(row, 6, "Total Purchase Cost", column_footer_style)
                    worksheet.write(row, 7, total_purchase_cost, column_footer_style)
                    row += 1
                else:
                    worksheet.write(row, 4, "Total Cost", column_footer_style)
                    worksheet.write(row, 5, total_sales_cost, column_footer_style)
                    row += 1

            fp = io.BytesIO()
            workbook.save(fp)
            excel_file = base64.encodestring(fp.getvalue())
            wizard.vendor_sales_report_file = excel_file
            wizard.file_name = 'Multi Vendor Sales Report for {} to {} generated on {}.xls'.format(self.from_date,
                                                                                                   self.to_date,
                                                                                                   datetime.now())
            wizard.vendor_sales_report_printed = True
            fp.close()
            return {
                'view_mode': 'form',
                'res_id': wizard.id,
                'res_model': 'vendor.product.sales.report.eg',
                'view_type': 'form',
                'type': 'ir.actions.act_window',
                'context': self.env.context,
                'target': 'new',
            }

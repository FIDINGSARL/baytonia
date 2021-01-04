import base64
import io
import logging
from datetime import datetime

import xlwt
from xlwt import easyxf

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class VendorDetailReport(models.TransientModel):
    _name = "vendor.detail.report.eg"

    vendor_ids = fields.Many2many("res.partner", string="Vendors")
    vendor_sales_report_file = fields.Binary('Invoice Report')
    vendor_detailed_report_printed = fields.Boolean('Invoice Report Printed')
    file_name = fields.Char('File Name')

    @api.multi
    def action_vendor_detail_report_eg(self):
        workbook = xlwt.Workbook()
        column_heading_style = easyxf(
            'font:height 200;font:bold True;pattern:pattern solid, fore_colour gray25 ;' "borders: top thin, bottom thin, left thin, right thin;")

        column_normal_style = easyxf(
            'font:height 200;' "borders: top thin, bottom thin, left thin, right thin;")

        vendor_names = ", ".join(self.vendor_ids.mapped("name"))
        worksheet = workbook.add_sheet("Vendor: {} Sales Report".format(vendor_names))
        worksheet.write_merge(0, 0, 0, 10, self.env.user.company_id.name,
                              easyxf(
                                  'font:height 200;font:bold True;align: horiz center;pattern:pattern solid, fore_colour gray25 ;'))

        hearder_counter = 0

        worksheet.write(2, hearder_counter, 'No.', column_heading_style)
        hearder_counter += 1

        worksheet.write(2, hearder_counter, 'Vendor Name ', column_heading_style)
        hearder_counter += 1

        worksheet.write(2, hearder_counter, 'Total Cost Purchase', column_heading_style)
        hearder_counter += 1

        worksheet.write(2, hearder_counter, 'Total Invoice Amount', column_heading_style)
        hearder_counter += 1

        worksheet.write(2, hearder_counter, 'Net Invoice Amount', column_heading_style)
        hearder_counter += 1

        worksheet.write(2, hearder_counter, 'Total Cost Sales ', column_heading_style)
        hearder_counter += 1

        worksheet.write(2, hearder_counter, 'Total Payment ', column_heading_style)
        hearder_counter += 1

        worksheet.write(2, hearder_counter, 'Net Total Payment ', column_heading_style)
        hearder_counter += 1

        worksheet.write(2, hearder_counter, 'Credit ', column_heading_style)
        hearder_counter += 1
        worksheet.write(2, hearder_counter, 'Total Stock ', column_heading_style)
        hearder_counter += 1
        # worksheet.write(2, hearder_counter, 'Avg Cost ', column_heading_style)
        # hearder_counter += 1
        worksheet.write(2, hearder_counter, 'Cost of Current Stock ', column_heading_style)
        hearder_counter += 1
        worksheet.write(2, hearder_counter, 'Profit', column_heading_style)
        hearder_counter += 1

        worksheet.col(0).width = 2000
        worksheet.col(1).width = 5500
        worksheet.col(2).width = 4500
        worksheet.col(3).width = 4500
        worksheet.col(4).width = 4000
        worksheet.col(5).width = 4000
        worksheet.col(6).width = 3600
        worksheet.col(7).width = 3600
        worksheet.col(8).width = 5000
        worksheet.col(9).width = 5000
        worksheet.col(10).width = 4000

        row = 3
        for wizard in self:
            sequence = 1
            for vendor_id in wizard.vendor_ids:
                supplierifo_ids = self.env['product.supplierinfo'].search([('name', '=', vendor_id.id)])
                vendor_name = vendor_id.name

                product_tmpl_ids = supplierifo_ids.mapped('product_tmpl_id')
                product_ids = product_tmpl_ids.mapped('product_variant_ids')

                # purchase_order_ids = self.env['purchase.order'].search(
                #     [('partner_id', '=', vendor_id.id), ('state', '!=', 'cancel')])
                # total_purchase_amount = sum(purchase_order_ids.mapped('amount_total'))

                vendor_invoices = self.env['account.invoice'].search(
                    [('partner_id', '=', vendor_id.id), ('type', '=', 'in_invoice'), ('state', '!=', 'cancel')])
                total_invoice_amount = sum(vendor_invoices.mapped('amount_total'))
                total_invoice_residual_amount = sum(vendor_invoices.mapped('residual'))
                vendor_return_invoices = self.env['account.invoice'].search(
                    [('partner_id', '=', vendor_id.id), ('type', '=', 'in_refund'), ('state', '!=', 'cancel')])
                total_invoice_return_amount = sum(vendor_return_invoices.mapped('amount_total'))
                net_invoice_amount = total_invoice_amount - total_invoice_return_amount
                total_payment = total_invoice_amount - total_invoice_residual_amount
                net_payment = total_invoice_amount - total_invoice_residual_amount + total_invoice_return_amount



                # total_stock = sum(product_ids.mapped('qty_available'))

                # if product_ids:
                #     avg_cost = sum(product_ids.mapped('standard_price')) / len(product_ids)
                # else:
                #     avg_cost = 0

                # cost_of_current_stock = total_stock * avg_cost

                total_sale_amount = 0
                total_purchase_amount = 0
                profit = 0
                qoh_cost = 0
                total_stock = 0
                for product_id in product_ids:
                    cost_price = product_id.standard_price
                    qty_available = product_id.qty_available
                    qoh_cost += qty_available * cost_price
                    total_stock += qty_available
                    sale_order_line_ids = self.env['sale.order.line'].search(
                        [('product_id', '=', product_id.id), ('state', 'in', ['done', 'sale'])])
                    for line in sale_order_line_ids:
                        delivered_qty = line.qty_delivered
                        # invoice_qty = line.qty_invoiced
                        sale_price = line.price_unit
                        total_profit = (sale_price - cost_price) * delivered_qty
                        profit += total_profit
                        # total_invoice_price = invoice_qty * cost_price
                        total_sale_amount += delivered_qty * cost_price
                    purchase_order_line_ids = self.env['purchase.order.line'].search(
                        [('product_id', '=', product_id.id), ('state', 'in', ['done', 'purchase'])])
                    for line in purchase_order_line_ids:
                        received_qty = line.qty_received
                        total_purchase_amount += received_qty * line.price_unit

                credit = total_purchase_amount - net_payment
                column_counter = 0
                worksheet.write(row, column_counter, sequence, column_normal_style)
                column_counter += 1
                worksheet.write(row, column_counter, vendor_name, column_normal_style)
                column_counter += 1
                worksheet.write(row, column_counter, round(total_purchase_amount, 2), column_normal_style)
                column_counter += 1
                worksheet.write(row, column_counter, round(total_invoice_amount, 2), column_normal_style)
                column_counter += 1
                worksheet.write(row, column_counter, round(net_invoice_amount, 2), column_normal_style)
                column_counter += 1
                worksheet.write(row, column_counter, round(total_sale_amount, 2), column_normal_style)
                column_counter += 1
                worksheet.write(row, column_counter, round(total_payment, 2), column_normal_style)
                column_counter += 1
                worksheet.write(row, column_counter, round(net_payment, 2), column_normal_style)
                column_counter += 1
                worksheet.write(row, column_counter, round(credit, 2), column_normal_style)
                column_counter += 1
                worksheet.write(row, column_counter, round(total_stock, 2), column_normal_style)
                column_counter += 1
                # worksheet.write(row, column_counter, round(avg_cost, 2), column_normal_style)
                # column_counter += 1
                worksheet.write(row, column_counter, round(qoh_cost, 2), column_normal_style)
                column_counter += 1
                worksheet.write(row, column_counter, round(profit, 2), column_normal_style)
                column_counter += 1
                row += 1
                sequence += 1

            fp = io.BytesIO()
            workbook.save(fp)
            excel_file = base64.encodestring(fp.getvalue())
            wizard.vendor_sales_report_file = excel_file

            wizard.file_name = 'Multi Vendor Detailed Report generated on {}.xls'.format(datetime.now())

            wizard.vendor_detailed_report_printed = True
            fp.close()
            return {
                'view_mode': 'form',
                'res_id': wizard.id,
                'res_model': 'vendor.detail.report.eg',
                'view_type': 'form',
                'type': 'ir.actions.act_window',
                'context': self.env.context,
                'target': 'new',
            }

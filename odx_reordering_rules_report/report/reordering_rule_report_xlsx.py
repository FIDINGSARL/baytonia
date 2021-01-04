from odoo import models, fields
import datetime
import io
import base64
import xlwt
from dateutil.relativedelta import relativedelta
from dateutil import parser
from statistics import median


LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


def excel_style(row, col):
    """ Convert given row and column number to an Excel-style cell name. """
    result = []
    while col:
        col, rem = divmod(col - 1, 26)
        result[:0] = LETTERS[rem]
    return ''.join(result) + str(row)


class ScrapReport(models.AbstractModel):
    _name = 'report.reordering.rule.report.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, wiz):

        # date_to = str(wiz.date_to) + ' ' + '23:59:59'
        # date_from = str(wiz.date_from) + ' ' + '00:00:00'
        #
        # scrap_orders = self.env['stock.scrap'].search(
        #     [('create_date', '<=', date_to), ('create_date', '>=', date_from)])

        heading_format = workbook.add_format({'align': 'center',
                                              'valign': 'vcenter',
                                              'bold': True, 'size': 15,
                                              # 'bg_color': '#0077b3',
                                              })
        sub_heading_format = workbook.add_format({'align': 'center',
                                                  'valign': 'vcenter',
                                                  'bold': True, 'size': 11,
                                                  # 'bg_color': '#0077b3',
                                                  # 'font_color': '#FFFFFF'
                                                  })

        col_format = workbook.add_format({'valign': 'left',
                                          'align': 'left',
                                          'bold': True,
                                          'size': 10,
                                          'font_color': '#000000'
                                          })
        data_format = workbook.add_format({'valign': 'center',
                                           'align': 'center',
                                           'size': 10,
                                           'font_color': '#000000'
                                           })

        col_format.set_text_wrap()
        worksheet = workbook.add_worksheet('Reordering Rule')
        worksheet.set_column('A:A', 5)
        worksheet.set_column('B:B', 40)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 10)
        worksheet.set_column('E:E', 10)
        worksheet.set_column('F:F', 20)
        worksheet.set_column('G:G', 30)
        worksheet.set_column('H:H', 30)
        worksheet.set_column('I:I', 20)
        worksheet.set_column('J:J', 20)
        worksheet.set_column('K:K', 20)
        worksheet.set_column('L:L', 30)
        worksheet.set_column('M:M', 30)
        row = 1
        worksheet.set_row(1, 20)
        starting_col = excel_style(row + 1, 1)
        ending_col = excel_style(row + 1, 9)
        # from_date = datetime.datetime.strptime(str(date_to), '%Y-%m-%d').strftime('%d/%m/%Y')
        # to_date = datetime.datetime.strptime(str(wiz.date_to), '%Y-%m-%d').strftime('%d/%m/%Y')
        row = row + 2

        # worksheet.merge_range('%s:%s' % (starting_col, ending_col),
        #                       "Scrap Orders" + " " + ':' + " " + from_date + " " + 'TO' + " " + to_date, heading_format)
        worksheet.write(row, 0, "Sl No", sub_heading_format)
        worksheet.write(row, 1, "Name", sub_heading_format)
        worksheet.write(row, 2, "QTY On Hand", sub_heading_format)
        worksheet.write(row, 3, "QTY Sold", sub_heading_format)
        worksheet.write(row, 4, "Sale Price", sub_heading_format)
        worksheet.write(row, 5, "Cost Price", sub_heading_format)
        worksheet.write(row, 6, "Last Cycle Sales / Day", sub_heading_format)
        worksheet.write(row, 7, "Avg Revenue / Day", sub_heading_format)
        worksheet.write(row, 8, "Max Sales /Day", sub_heading_format)
        worksheet.write(row, 9, "Min Sales /Day", sub_heading_format)
        worksheet.write(row, 10, "Median", sub_heading_format)
        worksheet.write(row, 11, "Profit Percentage", sub_heading_format)
        worksheet.write(row, 12, "Cumulativa Sales / Day", sub_heading_format)
        row += 1
        sl_no = 0
        supplier_info_ids = self.env['product.supplierinfo'].search([('name', 'in', wiz.vendor_ids.ids)])
        if supplier_info_ids:
            product_tmpl_ids = supplier_info_ids.mapped('product_tmpl_id')
            product_ids = product_tmpl_ids.mapped('product_variant_ids')

        else:
            product_ids = self.env["product.product"].search([])

        sale_price = []
        for product_id in product_ids:
            purcahse_dates = []
            purcahse_line_ids = self.env["purchase.order.line"].search(
                [("product_id", "=", product_id.id), ("order_id.state", "!=", "cancel"),
                 ('order_id.date_order', "<=", wiz.to_date)])
            for purcahse in purcahse_line_ids:
                purcahse_dates.append(purcahse.order_id.date_order)

            purcahse_dates.sort(key=lambda date: datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S"))

            if purcahse_line_ids:
                date_from = max(purcahse_dates)
                sale_order_ids = self.env["sale.order"].search(
                    [("confirmation_date", ">=", date_from), ("confirmation_date", "<=", wiz.to_date),
                     ("state", "!=", "cancel")])
                if sale_order_ids:
                    sale_line_ids = self.env["sale.order.line"].search(
                        [("product_id", "=", product_id.id), ("order_id", "in", sale_order_ids.ids)])
                    sale_qty = sum(sale_line_ids.mapped("product_uom_qty"))
                    if not sale_qty:
                        continue


                    cumilative_sales = 0
                    cumilative_days = 0

                    for i in range(1, len(purcahse_dates)):
                        cumilative_sale_order_ids = self.env["sale.order"].search(
                            [("confirmation_date", ">=", purcahse_dates[i-1]), ("confirmation_date", "<=", purcahse_dates[i]),
                             ("state", "!=", "cancel")])
                        if cumilative_sale_order_ids:
                            cumilative_sale_line_ids = self.env["sale.order.line"].search(
                                [("product_id", "=", product_id.id), ("order_id", "in", sale_order_ids.ids)])
                            cumilative_sale_qty = sum(sale_line_ids.mapped("product_uom_qty"))
                            if cumilative_sale_qty:
                                purcahse_start = datetime.datetime.strptime(purcahse_dates[i], "%Y-%m-%d %H:%M:%S")
                                purcahse_end = datetime.datetime.strptime(purcahse_dates[i-1], "%Y-%m-%d %H:%M:%S")
                                cumilative_day_range = (purcahse_start - purcahse_end).days
                                cumilative_sales += cumilative_sale_qty/cumilative_day_range if cumilative_day_range > 0 else 0


                    d1 = parser.parse(date_from).date()
                    d2 = parser.parse(wiz.to_date).date()
                    dates_btwn = d1
                    date_list = []
                    sale_per_day = []
                    sale_price = []
                    profict_percentage = 0

                    while dates_btwn <= d2:
                        dates_btwn = dates_btwn + relativedelta(days=1)
                        date_to_d = str(dates_btwn) + ' ' + '23:59:59'
                        date_from_d = str(dates_btwn) + ' ' + '00:00:00'
                        sale_order_ids_date = self.env["sale.order"].search(
                            [("confirmation_date", ">=", date_from_d), ("confirmation_date", "<=", date_to_d),
                             ("state", "!=", "cancel")])
                        sale_line_ids_date = self.env["sale.order.line"].search(
                            [("product_id", "=", product_id.id), ("order_id", "in", sale_order_ids_date.ids)])
                        if sale_line_ids_date:
                            sale_qty_date = sum(sale_line_ids_date.mapped("product_uom_qty"))
                            for sale in sale_line_ids_date:
                                sale_price.append(sale.price_unit)
                            if sale_qty_date:
                                date_list.append(dates_btwn)
                            sale_per_day.append(sale_qty_date)

                    sale_price.sort()

                    median_price = median(sale_price) if sale_price else 0
                    profict_percentage = ((
                                                  median_price - product_id.standard_price) / product_id.standard_price) * 100 if product_id.standard_price > 0 else 0

                    revenue = sale_qty * product_id.lst_price
                    from_date = datetime.datetime.strptime(date_from, "%Y-%m-%d %H:%M:%S")
                    to_date = datetime.datetime.strptime(wiz.to_date, "%Y-%m-%d")
                    duration_days = (to_date - from_date).days
                    avg_revenue_day = revenue / duration_days if duration_days > 0 else 0
                    avg_sale_day = sale_qty / duration_days if duration_days > 0 else 0
                    qoh = product_id.qty_available
                    if qoh < 1:
                        if date_list:
                            day_range = (date_list[-1] - from_date.date()).days if date_list else 0
                            avg_revenue_day = revenue / day_range if day_range != 0 else 0
                            avg_sale_day = sale_qty / day_range if day_range != 0 else 0
                    sl_no += 1
                    worksheet.write(row, 0, sl_no, data_format)
                    worksheet.write(row, 1, product_id.display_name, data_format)
                    worksheet.write(row, 2, qoh, data_format)
                    worksheet.write(row, 3, sale_qty, data_format)
                    worksheet.write(row, 4, product_id.lst_price, data_format)
                    worksheet.write(row, 5, product_id.standard_price, data_format)
                    worksheet.write(row, 6, avg_sale_day, data_format)
                    worksheet.write(row, 7, avg_revenue_day, data_format)
                    worksheet.write(row, 8, max(sale_per_day) if sale_per_day else 0, data_format)
                    worksheet.write(row, 9, min(sale_per_day) if sale_per_day else 0, data_format)
                    worksheet.write(row, 10, median_price, data_format)
                    worksheet.write(row, 11, profict_percentage, data_format)
                    worksheet.write(row, 12, cumilative_sales + avg_sale_day, data_format)
                    row += 1

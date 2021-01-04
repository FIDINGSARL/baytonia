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


class DateBatchReport(models.AbstractModel):
    _name = 'report.date.batch.report.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, wiz):
        date_to = str(wiz.to_date)
        date_from = str(wiz.from_date)



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
        worksheet = workbook.add_worksheet('Dispatching Barcode')
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
        tracking_barcodes = self.env['tracking.barcode'].search(
            [('dispaching_date', '<=', date_to), ('dispaching_date', '>=', date_from)])

        pickings =[]
        for tracking_barcode in tracking_barcodes:
            if tracking_barcode.picking_id not in pickings:
                pickings.append(tracking_barcode.picking_id)


        # from_date = datetime.datetime.strptime(str(date_to), '%Y-%m-%d').strftime('%d/%m/%Y')
        # to_date = datetime.datetime.strptime(str(wiz.date_to), '%Y-%m-%d').strftime('%d/%m/%Y')
        row = row + 2

        # worksheet.merge_range('%s:%s' % (starting_col, ending_col),
        #                       "Scrap Orders" + " " + ':' + " " + from_date + " " + 'TO' + " " + to_date, heading_format)
        worksheet.write(row, 0, "Sl No", sub_heading_format)
        worksheet.write(row, 1, "Tracking Ref", sub_heading_format)
        worksheet.write(row, 2, "Shipping Company", sub_heading_format)
        worksheet.write(row, 3, "Shipment No", sub_heading_format)
        worksheet.write(row, 4, "Dispatched By", sub_heading_format)
        worksheet.write(row, 5, "Dispatched Date", sub_heading_format)
        row += 1
        sl_no = 0

        for picking in pickings:
            tracking_barcodes = self.env['tracking.barcode'].search([('picking_id', '=', picking.id)])
            for tracking_barcode in tracking_barcodes:
                sl_no += 1
                worksheet.write(row, 0, sl_no, data_format)
                worksheet.write(row, 1, tracking_barcode.name, data_format)
                worksheet.write(row, 2,
                                tracking_barcode.shipping_company_id.name if tracking_barcode.shipping_company_id else '',
                                data_format)
                worksheet.write(row, 3, tracking_barcode.picking_id.name if tracking_barcode.picking_id else '',
                                data_format)
                worksheet.write(row, 4,
                                tracking_barcode.dispatched_user_id.name if tracking_barcode.dispatched_user_id else '',
                                data_format)
                worksheet.write(row, 5,
                                tracking_barcode.dispaching_date ,
                                data_format)

                row += 1

            row += 2

from odoo import models, fields
import datetime
import io
import base64
import xlwt

LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


def excel_style(row, col):
    """ Convert given row and column number to an Excel-style cell name. """
    result = []
    while col:
        col, rem = divmod(col - 1, 26)
        result[:0] = LETTERS[rem]
    return ''.join(result) + str(row)


class ScrapReport(models.AbstractModel):
    _name = 'report.scrap.report.report.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, wiz):

        date_to = str(wiz.date_to) + ' ' + '23:59:59'
        date_from = str(wiz.date_from) + ' ' + '00:00:00'

        scrap_orders = self.env['stock.scrap'].search(
            [('create_date', '<=', date_to), ('create_date', '>=', date_from)])

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
        worksheet = workbook.add_worksheet('Scrap Order')
        worksheet.set_column('A:A', 5)
        worksheet.set_column('B:B', 10)
        worksheet.set_column('C:C', 40)
        worksheet.set_column('D:D', 10)
        worksheet.set_column('E:E', 10)
        worksheet.set_column('F:F', 20)
        worksheet.set_column('G:G', 30)
        worksheet.set_column('H:H', 10)
        worksheet.set_column('I:I', 20)
        row = 1
        worksheet.set_row(1, 20)
        starting_col = excel_style(row + 1, 1)
        ending_col = excel_style(row + 1, 9)
        from_date = datetime.datetime.strptime(str(wiz.date_from), '%Y-%m-%d').strftime('%d/%m/%Y')
        to_date = datetime.datetime.strptime(str(wiz.date_to), '%Y-%m-%d').strftime('%d/%m/%Y')
        row = row + 2

        worksheet.merge_range('%s:%s' % (starting_col, ending_col),
                              "Scrap Orders" + " " + ':' + " " + from_date + " " + 'TO' + " " + to_date, heading_format)
        worksheet.write(row, 0, "Sl No", sub_heading_format)
        worksheet.write(row, 1, "Reference", sub_heading_format)
        worksheet.write(row, 2, "Product", sub_heading_format)
        worksheet.write(row, 3, "Price", sub_heading_format)
        worksheet.write(row, 4, "Cost", sub_heading_format)
        worksheet.write(row, 5, "Cause Of Damage", sub_heading_format)
        worksheet.write(row, 6, "Shipping Company", sub_heading_format)
        worksheet.write(row, 7, "Quantity", sub_heading_format)
        worksheet.write(row, 8, "Picking", sub_heading_format)
        worksheet.write(row, 9, "Responsible Person", sub_heading_format)
        row += 1
        sl_no = 0
        for scrap_order in scrap_orders:
            sl_no += 1
            user = False
            if scrap_order.picking_id:
                if scrap_order.picking_id.responsible_id:
                    user = True
            worksheet.write(row, 0, sl_no, data_format)
            worksheet.write(row, 1, scrap_order.name, data_format)
            worksheet.write(row, 2, scrap_order.product_id.name if scrap_order.product_id else " ", data_format)
            worksheet.write(row, 3, scrap_order.product_id.lst_price if scrap_order.product_id else " ", data_format)
            worksheet.write(row, 4, scrap_order.product_id.standard_price if scrap_order.product_id else " ",
                            data_format)
            worksheet.write(row, 5, scrap_order.cause_damage_id.name if scrap_order.cause_damage_id else " ", data_format)
            worksheet.write(row, 6, scrap_order.shipping_company_id.name if scrap_order.shipping_company_id else " ",
                            data_format)
            worksheet.write(row, 7, scrap_order.scrap_qty, data_format)
            worksheet.write(row, 8, scrap_order.picking_id.name if scrap_order.picking_id else " ", data_format)
            worksheet.write(row, 9, scrap_order.picking_id.responsible_id.name if user else " ", data_format)

            row += 1

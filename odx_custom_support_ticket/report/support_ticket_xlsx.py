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


class TicketReport(models.AbstractModel):
    _name = 'report.ticket.report.report.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, wiz):
        domain = []
        if wiz.date_to and wiz.date_from:
            from_date = datetime.datetime.strptime(str(wiz.date_from), '%Y-%m-%d').strftime('%d/%m/%Y')
            to_date = datetime.datetime.strptime(str(wiz.date_to), '%Y-%m-%d').strftime('%d/%m/%Y')
            date_to = str(wiz.date_to) + ' ' + '23:59:59'
            date_from = str(wiz.date_from) + ' ' + '00:00:00'
            domain.append(('create_date', '<=', date_to))
            domain.append(('create_date', '>=', date_from))
        if wiz.category:
            domain.append(('category', 'in', wiz.category.ids))

        if wiz.user:
            domain.append(('user_id', 'in', wiz.user.ids))
        tickets = self.env['website.support.ticket'].search(domain)


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
        worksheet = workbook.add_worksheet('Stock Move')
        worksheet.set_column('A:A', 5)
        worksheet.set_column('B:B', 40)
        worksheet.set_column('C:C', 30)
        worksheet.set_column('D:D', 30)
        worksheet.set_column('E:E', 30)
        worksheet.set_column('F:F', 20)
        worksheet.set_column('G:G', 20)
        worksheet.set_column('H:H', 20)
        worksheet.set_column('I:I', 20)
        row = 1
        worksheet.set_row(1, 20)
        starting_col = excel_style(row + 1, 1)
        ending_col = excel_style(row + 1, 9)

        row = row + 2
        if wiz.date_to and wiz.date_from:
            worksheet.merge_range('%s:%s' % (starting_col, ending_col),
                                  "Support Tickets" + " " + ':' + " " + from_date + " " + 'TO' + " " + to_date,
                                  heading_format)
        else:
            worksheet.merge_range('%s:%s' % (starting_col, ending_col),
                                  "Support Tickets",heading_format)
        worksheet.write(row, 0, "Sl No", sub_heading_format)
        worksheet.write(row, 1, "Ticket Number", sub_heading_format)
        worksheet.write(row, 2, "Person Name", sub_heading_format)
        worksheet.write(row, 3, "Category", sub_heading_format)
        worksheet.write(row, 4, "Sub Category", sub_heading_format)
        worksheet.write(row, 5, "User", sub_heading_format)
        worksheet.write(row, 6, "Days", sub_heading_format)
        worksheet.write(row, 7, "Hours", sub_heading_format)
        worksheet.write(row, 8, "Minutes", sub_heading_format)
        row += 1
        sl_no = 0
        total =0
        for ticket in tickets:
            sl_no += 1
            worksheet.write(row, 0, sl_no, data_format)
            worksheet.write(row, 1, ticket.ticket_number, data_format)
            worksheet.write(row, 2, ticket.partner_id.name if ticket.partner_id else ''  , data_format)
            worksheet.write(row, 3, ticket.category.name if ticket.category else '', data_format)
            worksheet.write(row, 4, ticket.sub_category_id.name if ticket.sub_category_id else '', data_format)

            for history in ticket.ticket_assign_history_ids:
                row += 1
                worksheet.write(row, 5, history.user_id.name if history.user_id else '',
                                data_format)
                worksheet.write(row, 6, str(history.days)  + " " + "Days" if history.days else str(0) + " " + "Days", data_format)
                worksheet.write(row, 7, str(history.hours)  + " " + "Hours" if history.hours else str(0) + " " + "Days", data_format)
                worksheet.write(row, 8, str(history.minutes)  + " " + "Minutes" if history.minutes else str(0) + " " + "Days", data_format)

                # total += history.duration
            row += 1
        # worksheet.write(row+1, 5, "Total", sub_heading_format)
        # worksheet.write(row+1, 6, str(total)+ " " + "Days", data_format)



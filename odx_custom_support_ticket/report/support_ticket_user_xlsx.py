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


class TicketUserReport(models.AbstractModel):
    _name = 'report.ticketuser.report.report.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, wiz):
        domain = []
        domain_user = []
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
            domain_user.append(('id', 'in', wiz.user.ids))

        tickets = self.env['website.support.ticket'].search(domain)
        users = self.env['res.users'].search(domain_user)

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
        worksheet.set_column('G:G', 10)
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
                                  "Support Tickets", heading_format)
        worksheet.write(row, 0, "Sl No", sub_heading_format)
        worksheet.write(row, 1, "User", sub_heading_format)
        worksheet.write(row, 2, "Number Of Ticket Created", sub_heading_format)
        worksheet.write(row, 3, "Number Of Ticket Assigned", sub_heading_format)
        worksheet.write(row, 4, "Number Of Ticket Closed", sub_heading_format)
        starting_col = excel_style(row + 1 , 6)
        ending_col = excel_style(row + 1 , 8)
        worksheet.merge_range('%s:%s' % (starting_col, ending_col),
                              "Average Duration", sub_heading_format)
        # worksheet.write(row, 5, "Average Duration", sub_heading_format)
        row += 1
        worksheet.write(row, 5, "Days", sub_heading_format)
        worksheet.write(row, 6, "Hours", sub_heading_format)
        worksheet.write(row, 7, "Minutes", sub_heading_format)
        row += 1

        sl_no = 0

        for user in users:
            created_count = 0
            assigned_count = 0
            closed_count = 0
            duration = 0
            hours = 0
            minutes = 0
            for ticket in tickets:
                if ticket.create_uid == user:
                    created_count += 1
                for assigned in ticket.ticket_assign_history_ids:
                    if assigned.user_id == user:
                        assigned_count += 1
                        duration += assigned.days
                        hours += assigned.hours
                        minutes += assigned.minutes
                        if minutes >= 60:
                            extra_hours = int(minutes / 60)
                            hours += extra_hours
                            minutes -= (extra_hours * 60)
                        if hours >= 24:
                            extra_day = int(hours / 24)
                            duration += extra_day
                            hours -= (extra_day * 24)
                        if assigned.end_date:
                            closed_count += 1
                        if assigned.end_date:
                            closed_count += 1

            sl_no += 1
            worksheet.write(row, 0, sl_no, data_format)
            worksheet.write(row, 1, user.name if user else '', data_format)
            worksheet.write(row, 2, created_count, data_format)
            worksheet.write(row, 3, assigned_count, data_format)
            worksheet.write(row, 4, closed_count, data_format)
            worksheet.write(row, 5, round(duration / closed_count,2) if closed_count != 0 else 0, data_format)
            worksheet.write(row, 6, round(hours / closed_count, 2) if closed_count != 0 else 0, data_format)
            worksheet.write(row, 7, round(minutes / closed_count, 2) if closed_count != 0 else 0, data_format)
            row += 1


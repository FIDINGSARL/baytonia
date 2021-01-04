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


class SurveyReport(models.AbstractModel):
    _name = 'report.survey.report.report.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, wiz):


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
        worksheet = workbook.add_worksheet('Survey Report')
        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:B', 30)
        worksheet.set_column('C:C', 30)
        worksheet.set_column('D:D', 30)
        worksheet.set_column('E:E', 30)
        worksheet.set_column('F:F', 30)
        worksheet.set_column('G:G', 30)
        worksheet.set_column('H:H', 30)
        worksheet.set_column('I:I', 30)
        worksheet.set_column('J:J', 30)
        worksheet.set_column('K:K', 30)
        worksheet.set_column('L:L', 30)
        worksheet.set_column('M:M', 30)
        worksheet.set_column('N:N', 30)
        worksheet.set_column('O:O', 30)
        row = 1
        worksheet.set_row(1, 20)
        head_row = row
        row = row + 2
        if wiz.page_ids:
            page = wiz.page_ids[0]
            UserInput = self.env['survey.user_input']
            complete_survey = UserInput.search([('survey_id', '=', wiz.id), ('state', '=', 'done')])
            i = 0
            for question in page.question_ids:
                ans_row = row + 1
                worksheet.write(row, i, question.question, sub_heading_format)
                for answer in complete_survey:
                    for user_input in answer.user_input_line_ids:
                        if user_input.question_id == question:
                            if user_input.answer_type == 'suggestion':
                                worksheet.write(ans_row, i,
                                                user_input.value_suggested.value if user_input.value_suggested else None,
                                                data_format)
                            elif user_input.answer_type == 'order':
                                worksheet.write(ans_row, i,
                                                user_input.order,
                                                data_format)
                            elif user_input.answer_type == 'ticket':
                                worksheet.write(ans_row, i,
                                                user_input.ticket,
                                                data_format)
                            elif user_input.answer_type == 'text':
                                worksheet.write(ans_row, i,
                                                user_input.value_text,
                                                data_format)
                            elif user_input.answer_type == 'free_text':
                                worksheet.write(ans_row, i,
                                                user_input.value_free_text,
                                                data_format)
                            elif user_input.answer_type == 'date':
                                worksheet.write(ans_row, i,
                                                user_input.value_date,
                                                data_format)
                            elif user_input.answer_type == 'number':
                                worksheet.write(ans_row, i,
                                                user_input.value_number,
                                                data_format)
                    ans_row += 1
                i += 1
        starting_col = excel_style(head_row + 1, 1)
        ending_col = excel_style(head_row + 1, i)
        worksheet.merge_range('%s:%s' % (starting_col, ending_col),
                              wiz.title, heading_format)
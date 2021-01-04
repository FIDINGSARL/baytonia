from odoo import models, fields


class CustomerSatisfactoryReport(models.AbstractModel):
    _name = 'report.customer.satisfactory.report.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, wiz):
        survey_inputs = self.env['survey.user_input_line'].search(
                        [('question_id.customer_support_survey', '=', True), ('value_suggested.value', '=', 'No')])
        ticket_list = []
        for rec in survey_inputs:
            res = dict()
            ticket_no = self.env['survey.user_input_line'].search(
                [('user_input_id', '=', rec.user_input_id.id), ('answer_type', '=', 'ticket')]).ticket
            reason = self.env['survey.user_input_line'].search(
                [('user_input_id', '=', rec.user_input_id.id), ('answer_type', '=', 'free_text')], limit=1)
            ticket_id = self.env['website.support.ticket'].search([('ticket_number', '=', ticket_no)])
            res['ticket_no'] = ticket_no
            res['customer'] = ticket_id.person_name
            res['email'] = ticket_id.email
            res['reason'] = reason.value_free_text
            ticket_list.append(res)

        heading_format = workbook.add_format({'align': 'center',
                                              'valign': 'vcenter',
                                              'bold': True, 'size': 18,
                                              # 'bg_color': '#0077b3',
                                              })
        head_line_format = workbook.add_format({'align': 'center',
                                                'valign': 'vcenter',
                                                'size': 4,
                                                # 'bg_color': '#9A9A9A',
                                                })

        sub_heading_format = workbook.add_format({'align': 'center',
                                                  'valign': 'vcenter',
                                                  'bold': True, 'size': 11,
                                                  'bg_color': '#0077b3',
                                                  # 'font_color': '#FFFFFF'
                                                  })

        data_format = workbook.add_format({'valign': 'center',
                                           'align': 'center',
                                           'size': 10,
                                           'font_color': '#000000'
                                           })

        # col_format.set_text_wrap()
        worksheet = workbook.add_worksheet('Customer Survey')
        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 50)

        worksheet.merge_range(0, 0, 0, 10, '', head_line_format)
        worksheet.write(0, 0, 'Customer Support Satisfactory Report', heading_format)

        worksheet.write(2, 0, "Ticket Number", sub_heading_format)
        worksheet.write(2, 1, "Customer Name", sub_heading_format)
        worksheet.write(2, 2, "Customer Email", sub_heading_format)
        worksheet.write(2, 3, "Explanation", sub_heading_format)

        row = 3
        for ticket in ticket_list:
            worksheet.write(row, 0, ticket.get('ticket_no'), data_format)
            worksheet.write(row, 1, ticket.get('customer'), data_format)
            worksheet.write(row, 2, ticket.get('email'), data_format)
            worksheet.write(row, 3, ticket.get('reason'), data_format)
            row += 1

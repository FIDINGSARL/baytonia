import base64
import datetime
import io

import xlwt
from xlwt import easyxf

from odoo import models, fields, api, _


class InvoiceReportEg(models.TransientModel):
    _name = "invoice.report.eg"

    @api.model
    def _get_from_date(self):
        company = self.env.user.company_id
        current_date = datetime.date.today()
        from_date = company.compute_fiscalyear_dates(current_date)['date_from']
        return from_date

    from_date = fields.Date(string='From Date', default=_get_from_date)
    to_date = fields.Date(string='To Date', default=datetime.date.today())
    invoice_report_file = fields.Binary('Invoice Report')
    file_name = fields.Char('File Name')
    invoice_report_printed = fields.Boolean('Invoice Report Printed')
    invoice_status = fields.Selection([('all', 'All'), ('paid', 'Paid'), ('un_paid', 'Unpaid')], string='Invoice State')

    @api.multi
    def action_invoice_report_eg(self):
        workbook = xlwt.Workbook()
        amount_tot = 0
        column_heading_style = easyxf('font:height 200;font:bold True;')
        worksheet = workbook.add_sheet('Invoice Report')
        worksheet.write(2, 3, self.env.user.company_id.name,
                        easyxf('font:height 200;font:bold True;align: horiz center;'))
        worksheet.write(4, 2, self.from_date, easyxf('font:height 200;font:bold True;align: horiz center;'))
        worksheet.write(4, 3, 'To', easyxf('font:height 200;font:bold True;align: horiz center;'))
        worksheet.write(4, 4, self.to_date, easyxf('font:height 200;font:bold True;align: horiz center;'))
        worksheet.write(6, 0, _('Invoice Number'), column_heading_style)
        worksheet.write(6, 1, _('Customer'), column_heading_style)
        worksheet.write(6, 2, _('Invoice Date'), column_heading_style)
        worksheet.write(6, 3, _('Invoice Amount'), column_heading_style)
        worksheet.write(6, 4, _('Invoice Currency'), column_heading_style)

        worksheet.col(0).width = 5000
        worksheet.col(1).width = 5000
        worksheet.col(2).width = 5000
        worksheet.col(3).width = 5000
        worksheet.col(4).width = 5000
        worksheet.col(5).width = 8000

        row = 7
        for wizard in self:
            customer_payment_data = {}
            heading = 'Invoice Report'
            worksheet.write_merge(0, 0, 0, 5, heading, easyxf(
                'font:height 210; align: horiz center;pattern: pattern solid, fore_color black; font: color white; font:bold True;' "borders: top thin,bottom thin"))
            if wizard.invoice_status == 'all':
                invoice_objs = self.env['account.invoice'].search([('date_invoice', '>=', wizard.from_date),
                                                                   ('date_invoice', '<=', wizard.to_date),
                                                                   ('type', '=', 'out_invoice'),
                                                                   ('state', 'not in', ['draft', 'cancel'])])
            elif wizard.invoice_status == 'paid':
                invoice_objs = self.env['account.invoice'].search([('date_invoice', '>=', wizard.from_date),
                                                                   ('date_invoice', '<=', wizard.to_date),
                                                                   ('state', '=', 'paid'),
                                                                   ('type', '=', 'out_invoice')])
            else:
                invoice_objs = self.env['account.invoice'].search([('date_invoice', '>=', wizard.from_date),
                                                                   ('date_invoice', '<=', wizard.to_date),
                                                                   ('state', '=', 'open'),
                                                                   ('type', '=', 'out_invoice')])
            for invoice in invoice_objs:
                amount = 0
                for journal_item in invoice.move_id.line_ids:
                    amount += journal_item.debit
                worksheet.write(row, 0, invoice.number)
                worksheet.write(row, 1, invoice.partner_id.name)
                worksheet.write(row, 2, invoice.date_invoice)
                worksheet.write(row, 3, invoice.amount_total)
                worksheet.write(row, 4, invoice.currency_id.symbol)
                amount_tot += amount
                row += 1
                key = u'_'.join((invoice.partner_id.name, invoice.currency_id.name)).encode('utf-8')
                key = str(key, 'utf-8')
                if key not in customer_payment_data:
                    customer_payment_data.update(
                        {key: {'amount_total': invoice.amount_total, 'amount_company_currency': amount}})
                else:
                    paid_amount_data = customer_payment_data[key]['amount_total'] + invoice.amount_total
                    amount_currency = customer_payment_data[key]['amount_company_currency'] + amount
                    customer_payment_data.update(
                        {key: {'amount_total': paid_amount_data, 'amount_company_currency': amount_currency}})
            worksheet.write(row + 2, 3, amount_tot, column_heading_style)

            fp = io.BytesIO()
            workbook.save(fp)
            excel_file = base64.encodestring(fp.getvalue())
            wizard.invoice_report_file = excel_file
            wizard.file_name = 'Invoice Report.xls'
            wizard.invoice_report_printed = True
            fp.close()
            return {
                'view_mode': 'form',
                'res_id': wizard.id,
                'res_model': 'invoice.report.eg',
                'view_type': 'form',
                'type': 'ir.actions.act_window',
                'context': self.env.context,
                'target': 'new',
            }

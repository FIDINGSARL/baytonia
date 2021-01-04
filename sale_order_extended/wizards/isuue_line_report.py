from odoo import models, fields, api
import xlwt
from io import BytesIO
from datetime import datetime, date, timedelta
import base64


class IssueLineReport(models.TransientModel):
    _name = "issue.line.report"

    @api.model
    def get_from_date(self):
        return date.today() - timedelta(days=7)

    from_date = fields.Date(string="From Date", default=get_from_date, required=True)
    to_date = fields.Date(string="To Date", default=date.today(), required=True)
    data = fields.Binary(readonly=True)
    file_name = fields.Char(string="File Name")

    @api.multi
    def generate_issue_line_report(self, from_cron=None):
        issue_line_ids = self.env["issue.line"].search(
            [("generate_date", ">=", self.from_date), ("generate_date", "<=", self.to_date)])
        serial_no = 1
        row = 0
        column = 0
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet("My Worksheet")
        duration = "{} to {}".format(self.from_date, self.to_date)
        header = xlwt.easyxf(
            "font: bold on, height 200;border:top thin,right thin,bottom thin,left thin; pattern:pattern solid, fore_colour gray25; alignment: horiz center ,vert center ")
        header1 = xlwt.easyxf(
            "font: bold on, height 300;border:top thin,right thin,bottom thin,left thin; pattern:pattern solid, fore_colour gray25; alignment: horiz center ,vert center ")
        header2 = xlwt.easyxf(
            "font: height 200;border:top thin,right thin,bottom thin,left thin; pattern:pattern solid, fore_colour gray25; alignment: horiz center ,vert center ")
        worksheet.write_merge(row, row, column, 10, duration, header1)
        row += 1
        worksheet.write_merge(row, row, column, 10, "Issue Line Report", header1)
        row += 2
        fnames = ["Serial No", "Order Name", "Issue Reason", "Product", "Quantity", "Unit Price", "Order Date",
                  "Issue Date", "Responsible Person", "Confirm By", "Shipping Company"]
        for header_name in fnames:
            worksheet.write(row, column, header_name, header)
            column += 1
        row += 1

        for issue_line_id in issue_line_ids:
            worksheet.write(row, 0, serial_no, header2)
            worksheet.write(row, 1, issue_line_id.order_id.name, header2)
            worksheet.write(row, 2, issue_line_id.reason_id.name, header2)
            worksheet.write(row, 3, issue_line_id.product_id.name, header2)
            worksheet.write(row, 4, issue_line_id.order_qty, header2)
            worksheet.write(row, 5, issue_line_id.unit_price, header2)
            worksheet.write(row, 6, issue_line_id.order_id.date_order, header2)
            worksheet.write(row, 7, issue_line_id.generate_date, header2)
            worksheet.write(row, 8, issue_line_id.responsible_id and issue_line_id.responsible_id.name or "",
                            header2)
            worksheet.write(row, 9, issue_line_id.confirm_person_id and issue_line_id.confirm_person_id.name or "",
                            header2)
            worksheet.write(row, 10, issue_line_id.carrier_id and issue_line_id.carrier_id.name or "",
                            header2)
            row += 1
            serial_no += 1

        fp = BytesIO()
        workbook.save(fp)
        fp.seek(0)
        file_new = base64.encodebytes(fp.read())

        fp.close()
        self.write({"data": file_new, "file_name": "issue_line_report"})
        if from_cron == "Weekly":
            # email code starts
            cron_emails_id = self.env["cron.emails"].search([("report_type", "=", "issue_line_report")],
                                                            limit=1)
            if cron_emails_id:
                attachment_name = "Issue Line Report {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))
                attachment_id = self.env['ir.attachment'].create({
                    'name': attachment_name,
                    'type': 'binary',
                    'datas': file_new,
                    'datas_fname': attachment_name + '.xls',
                    'store_fname': attachment_name,
                    'res_model': self._name,
                    'res_id': self.id,
                    'mimetype': 'application/x-xls'
                })
                # icpSudo = self.env['ir.config_parameter'].sudo()  # it is given all access
                # email = icpSudo.get_param('eg_product_supplier_report.email_id', default="")

                subject = "{} Issue Line Report".format(from_cron)

                body_html = "<p>Hello</p></b> Please check {} Issue Line Report for duration {}.</b><p>Thanks!!!</p>".format(
                    from_cron, duration)
                values = {
                    'model': None,
                    'res_id': None,
                    'subject': subject,
                    'body': '',
                    'body_html': body_html,
                    'parent_id': None,
                    'attachment_ids': [(6, 0, [attachment_id.id])] or None,
                    'email_from': "karam@baytonia.com",
                    'email_to': cron_emails_id.emails,
                }
                mail_id = self.env['mail.mail']
                mail_id.create(values).send()
        else:
            return {'type': "ir.actions.act_url",
                    'url': 'web/content/?model=issue.line.report&download=true&field=data&id=%s&filename=%s - %s.xls' % (
                        self.id, self.file_name, datetime.now().strftime("%Y-%m-%d")),
                    'target': 'self'}

    @api.multi
    def send_report_by_email(self):
        from_date = date.today() - timedelta(days=7)
        to_date = date.today()
        new_wizard = self.create({"from_date": from_date,
                                  "to_date": to_date}).generate_issue_line_report(from_cron="Weekly")

    @api.multi
    def generate_issue_line_on_screen_report(self):
        self.env['issue.line.screen.report'].search([]).unlink()
        data_dict = {}
        serial_no = 1
        issue_line_ids = self.env["issue.line"].search(
            [("generate_date", ">=", self.from_date), ("generate_date", "<=", self.to_date)])

        for line in issue_line_ids:
            data_dict.update({
                'serial_no': serial_no,
                'image_small':line.image_small,
                'order_id': line.order_id.id if line.order_id else False,
                'sale_line_id': line.sale_line_id.id if line.sale_line_id else False ,
                'product_id': line.product_id.id if line.product_id else False,
                'order_qty': line.order_qty,
                'unit_price': line.unit_price,
                'generate_date': line.generate_date,
                'responsible_id': line.responsible_id.id if line.responsible_id else False,
                'confirm_person_id': line.confirm_person_id.id if line.confirm_person_id else False,
                'carrier_id': line.carrier_id.id if line.carrier_id else False
            })
            serial_no += 1

            self.env['issue.line.screen.report'].create(data_dict)
        action = self.env.ref('sale_order_extended.action_issue_line_screen_report').read()[0]
        return action

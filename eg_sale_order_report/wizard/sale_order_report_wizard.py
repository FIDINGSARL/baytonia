import base64
from datetime import timedelta, date, datetime
from io import BytesIO

import xlwt

from odoo import models, fields, api


class SaleOrderReportWizard(models.TransientModel):
    _name = "sale.order.report.wizard"

    @api.model
    def _default_from_date(self):
        return date.today() - timedelta(days=7)

    # timedelta use for substract days

    to_date = fields.Date(string="To Date", default=date.today())
    from_date = fields.Date(string="From Date", default=_default_from_date)
    data = fields.Binary(string="Data", readonly=True)
    file_name = fields.Char(string="File Name")

    @api.multi
    def generate_report(self):
        sale_order_ids = self.env["sale.order"].search(
            [("confirmation_date", ">=", self.from_date), ("confirmation_date", "<=", self.to_date)])

        # serial_no = 1
        column = 0
        row = 0
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet("My Worksheet")
        fnames = ["Sale Order", "Confirmation Date", "SKU", "Product Name", 'Supplier', "Cost Price", "Sale Price",
                  "Total Sale Price",
                  "Quantity Sold", 'Profit', "Current QOH"]
        duration = self.from_date + " " + "to" + " " + self.to_date

        header = xlwt.easyxf(
            "font: bold on, height 200;border:top thin,right thin,bottom thin,left thin; pattern:pattern solid, fore_colour gray25; alignment: horiz center ,vert center ")
        header1 = xlwt.easyxf(
            "font: bold on, height 300;border:top thin,right thin,bottom thin,left thin; pattern:pattern solid, fore_colour gray25; alignment: horiz center ,vert center ")
        worksheet.write_merge(row, row, column, 10, duration, header1)
        row += 2

        for header_name in fnames:
            worksheet.write(row, column, header_name, header)
            column += 1
        row += 1

        for sale_order_id in sale_order_ids:

            for order_line_id in sale_order_id.order_line:
                if order_line_id.qty_delivered:
                    total_sale_price = order_line_id.qty_delivered * order_line_id.price_unit
                    total_cost_price = order_line_id.qty_delivered * order_line_id.product_id.standard_price
                    profit = total_sale_price - total_cost_price
                    confirm_date = datetime.strptime(sale_order_id.confirmation_date, '%Y-%m-%d %H:%M:%S').date()
                    worksheet.write(row, 0, sale_order_id.name)
                    worksheet.write(row, 1, str(confirm_date))
                    worksheet.write(row, 2, order_line_id.product_id.default_code)
                    worksheet.write(row, 3, order_line_id.product_id.name)
                    worksheet.write(row, 4,
                                    order_line_id.product_id.seller_ids and order_line_id.product_id.seller_ids[
                                        0].name.name or "")
                    worksheet.write(row, 5, order_line_id.product_id.standard_price)
                    worksheet.write(row, 6, order_line_id.price_unit)
                    worksheet.write(row, 7, total_sale_price)
                    worksheet.write(row, 8, order_line_id.qty_delivered)
                    worksheet.write(row, 9, profit)
                    worksheet.write(row, 10, order_line_id.product_id.qty_available)

                    row += 1
        # below use for download file
        fp = BytesIO()
        workbook.save(fp)
        fp.seek(0)
        file_new = base64.encodebytes(fp.read())

        fp.close()
        self.write({'data': file_new, 'file_name': "sale_order_report"})

        return {'type': "ir.actions.act_url",
                'url': 'web/content/?model=sale.order.report.wizard&download=true&field=data&id=%s&filename=%s - %s.xls' % (
                    self.id, self.file_name, datetime.now().strftime("%Y-%m-%d")),
                'target': 'self'}

    @api.multi
    def generate_report_for_sales_states(self, from_cron=None):
        if from_cron in ["Daily", "Weekly"]:
            if from_cron == "Daily":
                from_date = str(date.today() - timedelta(days=1)) + ' 00:00:00'
                to_date = str(date.today() - timedelta(days=1)) + ' 23:59:59'

            else:
                to_date = str(date.today())
                from_date = str(date.today() - timedelta(days=7))
        else:
            from_date = self.from_date
            to_date = self.to_date
        workbook = xlwt.Workbook()
        for state_type in ['Order Received', 'Confirmed']:
            if state_type == 'Order Received':
                sale_order_ids = self.env["sale.order"].search(
                    [("date_order", ">=", from_date), ("date_order", "<=", to_date)])
            else:
                sale_order_ids = self.env["sale.order"].search(
                    [("confirmation_date", ">=", from_date), ("confirmation_date", "<=", to_date)])
            serial_no = 1
            row = 0
            column = 0
            worksheet = workbook.add_sheet(state_type)
            duration = "{} to {}".format(from_date, to_date)
            header = xlwt.easyxf(
                "font: bold on, height 200;border:top thin,right thin,bottom thin,left thin; pattern:pattern solid, fore_colour gray25; alignment: horiz center ,vert center ")
            header1 = xlwt.easyxf(
                "font: bold on, height 300;border:top thin,right thin,bottom thin,left thin; pattern:pattern solid, fore_colour gray25; alignment: horiz center ,vert center ")
            header2 = xlwt.easyxf(
                "font: height 200;border:top thin,right thin,bottom thin,left thin; pattern:pattern solid, fore_colour gray25; alignment: horiz center ,vert center ")
            worksheet.write_merge(row, row, column, 5, duration, header1)
            row += 1
            worksheet.write_merge(row, row, column, 5, "Sales Report", header1)
            row += 2
            fnames = ["Serial No", "Order No", "Quotation Date", "Confirm Date", "Total Amount", "Expected Margin"]
            for header_name in fnames:
                worksheet.write(row, column, header_name, header)
                column += 1

            row += 1

            for sale_order_id in sale_order_ids:
                worksheet.write(row, 0, serial_no, header2)
                worksheet.write(row, 1, sale_order_id.name, header2)
                worksheet.write(row, 2, sale_order_id.date_order, header2)
                worksheet.write(row, 3, sale_order_id.confirmation_date, header2)
                worksheet.write(row, 4, sale_order_id.amount_total, header2)
                worksheet.write(row, 5, sale_order_id.margin, header2)
                row += 1
                serial_no += 1

        fp = BytesIO()
        workbook.save(fp)
        fp.seek(0)
        file_new = base64.encodebytes(fp.read())

        fp.close()
        self.write({"data": file_new, "file_name": "sales_states_report"})
        if from_cron in ["Daily", "Weekly"]:
            # email code starts
            attachment_name = "Sales states Report {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))
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

            subject = "{} Sales state Report".format(from_cron)

            body_html = "<p>Hello</p></b> Please find {} Sales report for duration {}.</b><p>Thanks</p>".format(
                from_cron, duration)
            values = {
                'model': None,
                'res_id': None,
                'subject': subject,
                'body': '',
                'body_html': body_html,
                'parent_id': None,
                'attachment_ids': [(6, 0, [attachment_id.id])] or None,
                'email_from': self.env.user.email or "karam@baytonia.com",
                'email_to': "karam@baytonia.com",
            }
            mail_id = self.env['mail.mail']
            mail_id.create(values).send()
        else:
            return {'type': "ir.actions.act_url",
                    'url': 'web/content/?model=sale.order.report.wizard&download=true&field=data&id=%s&filename=%s - %s.xls' % (
                        self.id, self.file_name, datetime.now().strftime("%Y-%m-%d")),
                    'target': 'self'}

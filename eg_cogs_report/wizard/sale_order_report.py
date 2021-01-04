from odoo import models, fields, api
from datetime import timedelta, date, datetime
import csv
import xlwt
import base64
from io import BytesIO
from odoo.exceptions import ValidationError


class SaleOrderReport(models.TransientModel):
    _name = "sale.order.report"

    @api.model
    def _default_from_date(self):
        return date.today() - timedelta(days=7)

    # timedelta use for substract days

    to_date = fields.Date(string="To Date", default=date.today())
    from_date = fields.Date(string="From Date", default=_default_from_date)
    data = fields.Binary(string="Data", readonly=True)
    file_name = fields.Char(string="File Name")

    @api.multi
    def generate_report_for_sale(self):
        sale_order_ids = self.env["sale.order"].search(
            [("confirmation_date", ">=", self.from_date), ("confirmation_date", "<=", self.to_date)])

        # serial_no = 1
        column = 0
        row = 0
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet("My Worksheet")
        fnames = ["Sale Order", "Product Name", 'Quantity', "Cost Price", "Total Cost Price"]
        duration = "{} to {}".format(self.from_date, self.to_date)

        header = xlwt.easyxf(
            "font: bold on, height 200;border:top thin,right thin,bottom thin,left thin; pattern:pattern solid, fore_colour gray25; alignment: horiz center ,vert center ")
        header1 = xlwt.easyxf(
            "font: bold on, height 300;border:top thin,right thin,bottom thin,left thin; pattern:pattern solid, fore_colour gray25; alignment: horiz center ,vert center ")
        header2 = xlwt.easyxf(
            "font: height 200;border:top thin,right thin,bottom thin,left thin; pattern:pattern solid, fore_colour gray25; alignment: horiz center ,vert center ")
        worksheet.write_merge(row, row, column, 4, duration, header1)
        row += 2

        for header_name in fnames:
            worksheet.write(row, column, header_name, header)
            column += 1
        row += 1

        for sale_order_id in sale_order_ids:

            for order_line_id in sale_order_id.order_line:
                if order_line_id.qty_delivered and order_line_id.product_id.type == "product":
                    total_cost_price = order_line_id.qty_delivered * order_line_id.product_id.standard_price
                    worksheet.write(row, 0, sale_order_id.name, header2)
                    worksheet.write(row, 1, order_line_id.product_id.name, header2)
                    worksheet.write(row, 2, order_line_id.qty_delivered, header2)
                    worksheet.write(row, 3, order_line_id.product_id.standard_price, header2)
                    worksheet.write(row, 4, total_cost_price, header2)

                    row += 1
        # below use for download file
        fp = BytesIO()
        workbook.save(fp)
        fp.seek(0)
        file_new = base64.encodebytes(fp.read())

        fp.close()
        self.write({'data': file_new, 'file_name': "new_sale_order_report"})

        return {'type': "ir.actions.act_url",
                'url': 'web/content/?model=sale.order.report&download=true&field=data&id=%s&filename=%s - %s.xls' % (
                    self.id, self.file_name, datetime.now().strftime("%Y-%m-%d")),
                'target': 'self'}

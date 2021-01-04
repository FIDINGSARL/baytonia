import base64
from datetime import timedelta, date, datetime
from io import BytesIO

import xlwt

from odoo import models, fields, api


class ProductPercentSaleReportWizard(models.TransientModel):
    _name = "product.percent.sale.report.wizard"

    @api.model
    def _default_from_date(self):
        return date.today() - timedelta(days=7)

    # timedelta use for substract days

    to_date = fields.Date(string="To Date", default=date.today())
    from_date = fields.Date(string="From Date", default=_default_from_date)
    data = fields.Binary(string="Data", readonly=True)
    file_name = fields.Char(string="File Name")
    type_of_qty = fields.Selection(
        [("ordered_qty", "Ordered Qty"), ("delivered_qty", "Delivered Qty"), ("invoiced_qty", "Invoiced Qty")],
        string="Type of Qty")
    with_profit = fields.Boolean(string="With Profit")
    with_percentage_on_total = fields.Boolean(string="Based on Total")

    @api.multi
    def generate_report(self):

        serial_no = 1
        column = 0
        row = 0
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet("My Worksheet")
        duration = self.from_date + " " + "to" + " " + self.to_date
        company_name = self.env.user.company_id.partner_id.name
        header = xlwt.easyxf(
            "font: bold on, height 200;border:top thin,right thin,bottom thin,left thin; pattern:pattern solid, fore_colour gray25; alignment: horiz center ,vert center ")
        header2 = xlwt.easyxf(
            "font:height 200;border:top thin,right thin,bottom thin,left thin; pattern:fore_colour gray25; alignment: horiz center ,vert center ")
        header1 = xlwt.easyxf(
            "font: bold on, height 300;border:top thin,right thin,bottom thin,left thin; pattern:pattern solid, fore_colour gray25; alignment: horiz center ,vert center ")
        header3 = xlwt.easyxf(
            "font: bold on, height 260;border:top thin,right thin,bottom thin,left thin; pattern:pattern solid, fore_colour gray25; alignment: horiz center ,vert center ")
        header4 = xlwt.easyxf(
            "font: bold on, height 230;border:top thin,right thin,bottom thin,left thin; pattern:pattern solid, fore_colour gray25; alignment: horiz center ,vert center ")
        fnames = []
        if self.with_profit:
            if self.with_percentage_on_total:
                fnames = ["Serial No", "Product Name", 'Sale Qty', "Based on Highest Sale %", "Based on Total Sale %",
                          "Profit", "Based on Highest Profit %", "Based on Total Profit %"]

            else:
                fnames = ["Serial No", "Product Name", 'Sale Qty', "Based on Highest Sale %", "Profit",
                          "Based on Highest Profit %"]

        if not self.with_profit:
            if self.with_percentage_on_total:
                fnames = ["Serial No", "Product Name", 'Sale Qty', "Based on Highest Sale %", "Based on Total Sale %"]

            else:
                fnames = ["Serial No", "Product Name", 'Sale Qty', "Based on Highest Sale %"]
        worksheet.write_merge(row, row, column, len(fnames) - 1, company_name, header1)
        row += 1
        worksheet.write_merge(row, row, column, len(fnames) - 1, duration, header3)
        row += 2

        for header_name in fnames:
            worksheet.write(row, column, header_name, header)
            column += 1
        row += 1
        high_sale = 0
        high_profit = 0
        total_sale = 0
        total_profit_report = 0
        list_of_dict = []
        product_ids = self.env["product.product"].search([("exclude_from_report", "=", False)])
        for product_id in product_ids:
            domain = [("product_id", "=", product_id.id), ("order_id.confirmation_date", ">=", self.from_date),
                      ("order_id.confirmation_date", "<=", self.to_date)]
            if self.type_of_qty == "ordered_qty":
                domain.append(("order_id.state", "in", ["done", "sale"]))

            sale_line_ids = self.env["sale.order.line"].search(domain)

            if not sale_line_ids:
                continue
            sale_qty = 0
            total_profit = 0
            if self.type_of_qty == "ordered_qty":
                sale_qty = sum(sale_line_ids.mapped("product_uom_qty"))
                if self.with_profit:
                    for sale_line_id in sale_line_ids:
                        total_profit += sale_line_id.price_unit * sale_line_id.product_uom_qty

            elif self.type_of_qty == "delivered_qty":
                sale_qty = sum(sale_line_ids.mapped("qty_delivered"))
                if self.with_profit:
                    for sale_line_id in sale_line_ids:
                        total_profit += sale_line_id.price_unit * sale_line_id.qty_delivered

            elif self.type_of_qty == "invoiced_qty":
                sale_qty = sum(sale_line_ids.mapped("qty_invoiced"))
                if self.with_profit:
                    for sale_line_id in sale_line_ids:
                        total_profit += sale_line_id.price_unit * sale_line_id.qty_invoiced

            if sale_qty > high_sale:
                high_sale = sale_qty
            if self.with_percentage_on_total:
                total_sale += sale_qty

            if total_profit > high_profit:
                high_profit = total_profit
            if self.with_percentage_on_total:
                total_profit_report += total_profit

            product_dict = {"product_name": product_id.name,
                            "sale_qty": sale_qty,
                            "profit": total_profit}
            list_of_dict.append(product_dict)

        for product_dict in list_of_dict:
            sale_percentage = 0
            total_sale_percentage = 0
            if high_sale:
                sale_percentage = round((product_dict.get("sale_qty") * 100) / high_sale, 2)
            if total_sale:
                total_sale_percentage = round((product_dict.get("sale_qty") * 100) / total_sale, 2)
            worksheet.write(row, 0, serial_no, header2)
            worksheet.write(row, 1, product_dict.get("product_name"), header2)
            worksheet.write(row, 2, product_dict.get("sale_qty"), header2)
            worksheet.write(row, 3, sale_percentage, header2)
            if self.with_profit:
                profit_percentage = 0
                total_profit_percentage = 0
                if high_profit:
                    profit_percentage = round((product_dict.get("profit") * 100) / high_profit, 2)

                if self.with_percentage_on_total:
                    if total_profit_report:
                        total_profit_percentage = round((product_dict.get("profit") * 100) / total_profit_report, 2)
                    worksheet.write(row, 4, total_sale_percentage, header2)
                    worksheet.write(row, 5, product_dict.get("profit"), header2)
                    worksheet.write(row, 6, profit_percentage, header2)
                    worksheet.write(row, 7, total_profit_percentage, header2)
                else:
                    worksheet.write(row, 4, product_dict.get("profit"), header2)
                    worksheet.write(row, 5, profit_percentage, header2)
            else:
                if self.with_percentage_on_total:
                    worksheet.write(row, 4, total_sale_percentage, header2)

            row += 1
            serial_no += 1

        # below use for download file
        fp = BytesIO()
        workbook.save(fp)
        fp.seek(0)
        file_new = base64.encodebytes(fp.read())

        fp.close()
        self.write({'data': file_new, 'file_name': "product_percent_sale_report"})

        return {'type': "ir.actions.act_url",
                'url': 'web/content/?model=product.percent.sale.report.wizard&download=true&field=data&id=%s&filename=%s - %s.xls' % (
                    self.id, self.file_name, datetime.now().strftime("%Y-%m-%d")),
                'target': 'self'}

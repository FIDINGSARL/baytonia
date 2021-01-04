from odoo import models, fields, api
import base64
import xlwt
from io import BytesIO
from datetime import datetime, date, timedelta


class SpecialDeliveryReport(models.TransientModel):
    _name = "special.delivery.report"

    @api.model
    def default_set_from(self):
        return date.today() - timedelta(days=7)

    @api.model
    def default_set_delivery_status_id(self):
        delivery_status_id = self.env["stock.picking.status"].search([("name", "like", "Special delivery")], limit=1)
        return delivery_status_id and delivery_status_id.id or None

    # from_date = fields.Date(string="From Date", default=default_set_from, required=True)
    # to_date = fields.Date(string="To Date", default=date.today(), required=True)
    data = fields.Binary(string="Data", readonly=True)
    file_name = fields.Char(string="File Name")
    delivery_status_id = fields.Many2one(comodel_name="stock.picking.status", string="Delivery Status", required=True,
                                         default=default_set_delivery_status_id)

    @api.multi
    def make_special_delivery_report(self):
        picking_ids = self.env["stock.picking"].search(
            [("delivery_status_id", "=", self.delivery_status_id.id)])

        serial_no = 1
        # duration = "{} to {}".format(self.from_date, self.to_date)
        column = 0
        row = 0
        report_name = "{} Report".format(self.delivery_status_id.name)
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet(report_name)
        header = xlwt.easyxf(
            "font: bold on, height 200;border:top thin,right thin,bottom thin,left thin; pattern:pattern solid, fore_colour gray25; alignment: horiz center ,vert center ")
        header2 = xlwt.easyxf(
            "font:height 200;border:top thin,right thin,bottom thin,left thin; pattern:fore_colour gray25; alignment: horiz center ,vert center ")
        header1 = xlwt.easyxf(
            "font: bold on, height 300;border:top thin,right thin,bottom thin,left thin; pattern:pattern solid, fore_colour gray25; alignment: horiz center ,vert center ")
        header_names = ["Serial No", "Name", "Customer", "City", "Address", "Number", "Source Document",
                        "Scheduled Date", "Boxes"]
        worksheet.write_merge(row, row, column, 8, report_name, header1)
        row += 1
        # # worksheet.write_merge(row, row, column, 8, duration, header1)
        # row += 2
        for header_name in header_names:
            worksheet.write(row, column, header_name, header)
            column += 1
        row += 1
        for picking_id in picking_ids:
            address = "{}, {}".format(picking_id.partner_id.street,
                                      picking_id.partner_id.street2 and picking_id.partner_id.street2 or "")
            worksheet.write(row, 0, serial_no, header2)
            worksheet.write(row, 1, picking_id.name, header2)
            worksheet.write(row, 2, picking_id.partner_id.name, header2)
            worksheet.write(row, 3, picking_id.partner_id.city, header2)
            worksheet.write(row, 4, address, header2)
            worksheet.write(row, 5, picking_id.partner_id.phone, header2)
            worksheet.write(row, 6, picking_id.origin, header2)
            worksheet.write(row, 7, picking_id.scheduled_date, header2)
            worksheet.write(row, 8, picking_id.boxes, header2)
            row += 1
            serial_no += 1
        fp = BytesIO()
        workbook.save(fp)
        fp.seek(0)
        file_new = base64.encodebytes(fp.read())

        fp.close()
        self.write({'data': file_new, 'file_name': "special_delivery_report"})

        return {'type': "ir.actions.act_url",
                'url': 'web/content/?model=special.delivery.report&download=true&field=data&id=%s&filename=%s - %s.xls' % (
                    self.id, self.file_name, datetime.now().strftime("%Y-%m-%d")),
                'target': 'self'}

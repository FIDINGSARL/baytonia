import base64
from datetime import datetime, date, timedelta
from io import BytesIO

import xlwt

from odoo import models, fields, api


class PickingBarcodeReport(models.TransientModel):
    _name = "picking.barcode.report"

    @api.model
    def _set_from_date(self):
        return date.today() - timedelta(days=7)

    to_date = fields.Date(string="To Date", default=date.today())
    from_date = fields.Date(string="From Date", default=_set_from_date)
    data = fields.Binary(string="Data")
    file_name = fields.Char(string="File Name")

    @api.multi
    def generate_report_for_inventory(self, from_cron=None):
        if from_cron in ["Daily", "Weekly"]:
            if from_cron == "Daily":
                from_date = str(date.today() - timedelta(days=1))
                to_date = str(date.today() - timedelta(days=1))

            else:
                to_date = str(date.today())
                from_date = str(date.today() - timedelta(days=7))
        else:
            from_date = self.from_date
            to_date = self.to_date

        stock_picking_ids = self.env["stock.picking"].search(
            [("date_done", ">=", from_date), ("date_done", "<=", to_date)])
        serial_no = 1
        row = 0
        column = 0
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet("My Worksheet")
        duration = "{} to {}".format(from_date, to_date)
        header = xlwt.easyxf(
            "font: bold on, height 200;border:top thin,right thin,bottom thin,left thin; pattern:pattern solid, fore_colour gray25; alignment: horiz center ,vert center ")
        header1 = xlwt.easyxf(
            "font: bold on, height 300;border:top thin,right thin,bottom thin,left thin; pattern:pattern solid, fore_colour gray25; alignment: horiz center ,vert center ")
        header2 = xlwt.easyxf(
            "font: height 200;border:top thin,right thin,bottom thin,left thin; pattern:pattern solid, fore_colour gray25; alignment: horiz center ,vert center ")
        worksheet.write_merge(row, row, column, 7, duration, header1)
        row += 1
        worksheet.write_merge(row, row, column, 7, "Barcode Scan Report", header1)
        row += 2
        fnames = ["Serial No", "Name", "Barcode Scan", "Responsible Person","Order Date","Done Time","Dispatch Time","Dispatch - Done time"]
        for header_name in fnames:
            worksheet.write(row, column, header_name, header)
            column += 1

        row += 1
        responsible_info_list = []
        responsible_person_list = []
        so_list = []
        po_list = []
        return_po_list = []
        return_so_list = []

        for stock_picking_id in stock_picking_ids:
            if stock_picking_id.barcode_scan:
                barcode_scan = "Yes"
            else:
                barcode_scan = "No"

            tracking_barcode = self.env["tracking.barcode"].search(
                [("picking_id", "=", stock_picking_id.id)],limit=1)
            duration_days =0
            if tracking_barcode and tracking_barcode.dispaching_date :
                from_date = datetime.strptime(stock_picking_id.date_done, "%Y-%m-%d %H:%M:%S")
                to_date = datetime.strptime(tracking_barcode.dispaching_date, "%Y-%m-%d")
                duration_days = (to_date - from_date).days
            responsible = stock_picking_id.responsible_id and stock_picking_id.responsible_id.name or ""
            worksheet.write(row, 0, serial_no, header2)
            worksheet.write(row, 1, stock_picking_id.name, header2)
            worksheet.write(row, 2, barcode_scan, header2)
            worksheet.write(row, 3, responsible,
                            header2)
            worksheet.write(row, 4, stock_picking_id.scheduled_date, header2)
            worksheet.write(row, 5, stock_picking_id.date_done, header2)
            worksheet.write(row, 6, tracking_barcode.dispaching_date if tracking_barcode else False, header2)
            worksheet.write(row, 7, duration_days, header2)
            if responsible:
                responsible_info_list.append(responsible)
                if stock_picking_id.picking_type_code == "incoming":
                    if stock_picking_id.purchase_id:
                        po_list.append(responsible)
                    else:
                        return_so_list.append(responsible)
                else:
                    if stock_picking_id.sale_id:
                        so_list.append(responsible)
                    else:
                        return_po_list.append(responsible)
                if responsible not in responsible_person_list:
                    responsible_person_list.append(responsible)
            row += 1
            serial_no += 1
        row += 2
        serial_no = 1
        worksheet.write(row, 0, "Serial No", header)
        worksheet.write(row, 1, "Responsible Person", header)
        worksheet.write(row, 2, "Total Process Count", header)
        worksheet.write(row, 3, "Total Purchase Incoming", header)
        worksheet.write(row, 4, "Total Sale Outgoing", header)
        worksheet.write(row, 5, "Total Purchase Return", header)
        worksheet.write(row, 6, "Total Sale Return", header)

        row += 1
        total_dict = {"sum_count": 0, "sum_po": 0, "sum_so": 0, "sum_po_return": 0, "sum_so_return": 0}
        for responsible_person in responsible_person_list:
            count = responsible_info_list.count(responsible_person)
            total_so = so_list.count(responsible_person)
            total_so_return = return_so_list.count(responsible_person)
            total_po = po_list.count(responsible_person)
            total_po_return = return_po_list.count(responsible_person)
            total_dict["sum_count"] = total_dict.get("sum_count") + count
            total_dict["sum_po"] = total_dict.get("sum_po") + total_po
            total_dict["sum_so"] = total_dict.get("sum_so") + total_so
            total_dict["sum_po_return"] = total_dict.get("sum_po_return") + total_po_return
            total_dict["sum_so_return"] = total_dict.get("sum_so_return") + total_so_return
            worksheet.write(row, 0, serial_no, header2)
            worksheet.write(row, 1, responsible_person, header2)
            worksheet.write(row, 2, count, header2)
            worksheet.write(row, 3, total_po, header2)
            worksheet.write(row, 4, total_so, header2)
            worksheet.write(row, 5, total_po_return, header2)
            worksheet.write(row, 6, total_so_return, header2)
            serial_no += 1
            row += 1
        row += 1
        worksheet.write(row, 1, "Sum of Column", header)
        worksheet.write(row, 2, total_dict.get("sum_count"), header2)
        worksheet.write(row, 3, total_dict.get("sum_po"), header2)
        worksheet.write(row, 4, total_dict.get("sum_so"), header2)
        worksheet.write(row, 5, total_dict.get("sum_po_return"), header2)
        worksheet.write(row, 6, total_dict.get("sum_so_return"), header2)

        fp = BytesIO()
        workbook.save(fp)
        fp.seek(0)
        file_new = base64.encodebytes(fp.read())

        fp.close()
        self.write({"data": file_new, "file_name": "picking_barcode_report"})
        if from_cron in ["Daily", "Weekly"]:
            # email code starts
            attachment_name = "Picking Barcode Report {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))
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
            icpSudo = self.env['ir.config_parameter'].sudo()  # it is given all access
            email = icpSudo.get_param('eg_product_supplier_report.email_id', default="")

            subject = "{} Picking Barcode Report".format(from_cron)

            body_html = "<p>Hello</p></b> Please find {} Barcode scan report for duration {}.</b><p>Thanks</p>".format(
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
                'email_to': email,
            }
            mail_id = self.env['mail.mail']
            mail_id.create(values).send()
        else:
            return {'type': "ir.actions.act_url",
                    'url': 'web/content/?model=picking.barcode.report&download=true&field=data&id=%s&filename=%s - %s.xls' % (
                        self.id, self.file_name, datetime.now().strftime("%Y-%m-%d")),
                    'target': 'self'}

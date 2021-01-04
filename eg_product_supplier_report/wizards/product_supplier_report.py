from odoo import models, fields, api
from datetime import datetime, date, timedelta
import xlwt
import base64
from io import BytesIO


class ProductSupplierReport(models.TransientModel):
    _name = "product.supplier.report"

    file_name = fields.Char(string="File Name")
    data = fields.Binary(string="Data")
    list_without_vendor = fields.Boolean(string="List Without Vendor Product")

    @api.multi
    def generate_without_vendor_product(self, from_cron=None):
        current_date = date.today()

        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet("My Worksheet")
        header2 = xlwt.easyxf(
            "font:height 200;border:top thin,right thin,bottom thin,left thin; pattern:fore_colour gray25; alignment: horiz center ,vert center ")
        header1 = xlwt.easyxf(
            "font: bold on, height 300;border:top thin,right thin,bottom thin,left thin; pattern:pattern solid, fore_colour gray25; alignment: horiz center ,vert center ")
        header3 = xlwt.easyxf(
            "font: bold on, height 260;border:top thin,right thin,bottom thin,left thin; pattern:pattern solid, fore_colour gray25; alignment: horiz center ,vert center ")
        serial_no = 1
        row = 0
        column = 0
        if self.list_without_vendor:
            worksheet.write_merge(row, row, column, 2, "List Of Product Without vendor", header1)
            row += 2
            worksheet.write_merge(row, row, column, 2, str(current_date), header1)
            row += 2
        else:
            worksheet.write_merge(row, row, column, 3, "List Of Product Without vendor", header1)
            row += 2
            worksheet.write_merge(row, row, column, 3, str(current_date), header1)
            row += 2
        fnames = ["Serial No", "Name", "SKU"]
        if not self.list_without_vendor:
            fnames.append("Vendor Name")
        for header_name in fnames:
            worksheet.write(row, column, header_name, header3)
            column += 1
        row += 1
        product_ids = self.env["product.template"].search([])
        if self.list_without_vendor:
            product_ids = product_ids.filtered(lambda l: not l.seller_ids.mapped("name"))
        for product_id in product_ids:
            worksheet.write(row, 0, serial_no, header2)
            worksheet.write(row, 1, product_id.name, header2)
            worksheet.write(row, 2, product_id.default_code or "", header2)
            if not self.list_without_vendor:
                worksheet.write(row, 3, product_id.seller_ids and product_id.seller_ids[0].name.name or "")
            row += 1
            serial_no += 1

        fp = BytesIO()
        workbook.save(fp)
        fp.seek(0)
        file_new = base64.encodebytes(fp.read())
        fp.close()
        self.write({'data': file_new, 'file_name': "list_without_vendor_product"})
        if from_cron:
            # email code starts
            attachment_name = "Product Supplier Report {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))
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

            values = {
                'model': None,
                'res_id': None,
                'subject': "Weekly Product Supplier Report",
                'body': '',
                'body_html': "",
                'parent_id': None,
                'attachment_ids': [(6, 0, [attachment_id.id])] or None,
                'email_from': "",
                'email_to': email,
                'email_cc': ""
            }
            mail_id = self.env['mail.mail']
            mail_id.create(values).send()
        if not from_cron:
            return {'type': "ir.actions.act_url",
                    'url': 'web/content/?model=product.supplier.report&download=true&field=data&id=%s&filename=%s - %s.xls' % (
                        self.id, self.file_name, datetime.now().strftime("%Y-%m-%d")),
                    'target': 'self'}

import base64
from datetime import datetime, date
from io import BytesIO

import xlwt

from odoo import models, fields, api


class HpMTOReport(models.TransientModel):
    _name = "hp.mto.report"

    file_name = fields.Char(string="File Name")
    data = fields.Binary(string="Data")

    @api.multi
    def generate_on_screen_report(self):
        self.env['hp.mto.line'].search([]).unlink()
        current_date = date.today()
        serial_no = 1
        mto_id = self.env.ref('stock.route_warehouse0_mto')
        product_ids = self.env["product.product"].search([("route_ids", "in", [mto_id.id])])
        for product_id in product_ids:
            list_dict = {}
            if product_id.categ_ids:
                category_list = [category_id.display_name for category_id in product_id.categ_ids]
            else:
                category_list = [""]
            for category in category_list:
                list_dict.update({
                    'serial_no': serial_no,
                    'product_id': product_id.id,
                    'image_small': product_id.image_small,
                    'qty_available': product_id.qty_available,
                    'category': category,
                })
            serial_no += 1
            self.env['hp.mto.line'].create(list_dict)

        action = self.env.ref('eg_hero_product_report.action_hero_product_line').read()[0]
        return action

    @api.multi
    def generate_mto_product_report(self):
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

        worksheet.write_merge(row, row, column, 3, "List Of MTO Product", header1)
        row += 2
        worksheet.write_merge(row, row, column, 3, str(current_date), header1)
        row += 2

        fnames = ["Serial No", "Name", "Quantity", "Category"]
        for header_name in fnames:
            worksheet.write(row, column, header_name, header3)
            column += 1
        row += 1
        mto_id = self.env.ref('stock.route_warehouse0_mto')
        product_ids = self.env["product.product"].search([("route_ids", "in", [mto_id.id])])
        for product_id in product_ids:
            if product_id.categ_ids:
                category_list = [category_id.display_name for category_id in product_id.categ_ids]
            else:
                category_list = [""]
            for category in category_list:
                worksheet.write(row, 0, serial_no, header2)
                worksheet.write(row, 1, product_id.name, header2)
                worksheet.write(row, 2, product_id.qty_available, header2)
                worksheet.write(row, 3, category, header2)
                row += 1

            serial_no += 1

        fp = BytesIO()
        workbook.save(fp)
        fp.seek(0)
        file_new = base64.encodebytes(fp.read())
        fp.close()
        self.write({'data': file_new, 'file_name': "hp_mto_report"})

        return {'type': "ir.actions.act_url",
                'url': 'web/content/?model=hp.mto.report&download=true&field=data&id=%s&filename=%s - %s.xls' % (
                    self.id, self.file_name, datetime.now().strftime("%Y-%m-%d")),
                'target': 'self'}

import base64
import io

import xlwt
from xlwt import easyxf

from odoo import models, fields, api


class DeliveryCompanyReportWizard(models.TransientModel):
    _name = "delivery.company.report.wizard"

    delivery_carrier = fields.Many2one("delivery.carrier", "Delivery Company")
    delivery_report_file = fields.Binary('Invoice Report')
    delivery_report_printed = fields.Boolean('Invoice Report Printed')
    file_name = fields.Char('File Name')
    date_from = fields.Datetime("From")
    date_to = fields.Datetime("To")
    only_today = fields.Boolean("Today")

    @api.multi
    def action_delivery_report_eg(self):
        workbook = xlwt.Workbook()
        date_from = self.date_from
        date_to = self.date_to
        column_heading_style = easyxf(
            'font:height 200;font:bold True;' "borders: top thin, bottom thin, left thin, right thin;")
        column_footer_style = easyxf(
            'font:height 200;font:bold True;')
        column_normal_style = easyxf(
            'font:height 200;' "borders: top thin, bottom thin, left thin, right thin;")
        worksheet = workbook.add_sheet("{} Shipment Manifest".format(self.delivery_carrier.name))
        worksheet.write(2, 1, self.env.user.company_id.name,
                        easyxf('font:height 200;font:bold True;align: horiz center;'))
        worksheet.write(4, 0, date_from, easyxf('font:height 200;font:bold True;align: horiz center;'))
        worksheet.write(4, 1, 'To', easyxf('font:height 200;font:bold True;align: horiz center;'))
        worksheet.write(4, 2, date_to, easyxf('font:height 200;font:bold True;align: horiz center;'))
        worksheet.write(6, 0, 'Delivery Number', column_heading_style)
        worksheet.write(6, 1, 'Customer Name', column_heading_style)
        worksheet.write(6, 2, 'Tracking Ref', column_heading_style)
        worksheet.write(6, 3, 'Boxes', column_heading_style)
        # worksheet.write(6, 4, 'Other', column_heading_style)

        worksheet.col(0).width = 5000
        worksheet.col(1).width = 5000
        worksheet.col(2).width = 5000
        worksheet.col(3).width = 5000
        worksheet.col(4).width = 5000
        worksheet.col(5).width = 8000

        row = 7
        for wizard in self:
            heading = "{} Shipment Manifest".format(wizard.delivery_carrier.name)
            worksheet.write_merge(0, 0, 0, 3, heading, easyxf(
                'font:height 210; align: horiz center;pattern: pattern solid,'
                ' fore_color black; font: color white; font:bold True;' "borders: top thin,bottom thin"))
            picking_ids = self.env['stock.picking'].search(
                [('carrier_id', '=', self.delivery_carrier.id), ('scheduled_date', '>=', date_from),
                 ('scheduled_date', '<=', date_to), ('state', '=', 'done')])
            boxes = 0
            for picking_id in picking_ids:
                worksheet.write(row, 0, picking_id.name, column_normal_style)
                worksheet.write(row, 1, picking_id.partner_id.name, column_normal_style)
                worksheet.write(row, 2, picking_id.carrier_tracking_ref, column_normal_style)
                worksheet.write(row, 3, picking_id.boxes, column_normal_style)
                boxes += picking_id.boxes
                # worksheet.write(row, 4, "")
                row += 1
            worksheet.write(row, 2, "Total Boxes", column_footer_style)
            worksheet.write(row, 3, boxes, column_footer_style)
            row += 1
            worksheet.write(row + 2, 0, "Pickup Person's Name", column_footer_style)
            worksheet.write(row + 2, 2, "Pickup Person's Signature", column_footer_style)

            fp = io.BytesIO()
            workbook.save(fp)
            excel_file = base64.encodestring(fp.getvalue())
            wizard.delivery_report_file = excel_file
            wizard.file_name = '{} Shipment Manifest.xls'.format(self.delivery_carrier.name)
            wizard.delivery_report_printed = True
            fp.close()
            return {
                'view_mode': 'form',
                'res_id': wizard.id,
                'res_model': 'delivery.company.report.wizard',
                'view_type': 'form',
                'type': 'ir.actions.act_window',
                'context': self.env.context,
                'target': 'new',
            }

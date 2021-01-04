import base64
from datetime import datetime, date, timedelta
from io import BytesIO

import xlwt

from odoo import models, fields, api

class StockScrapReportWiz(models.TransientModel):
    _name = "stock.scrap.report.wiz"

    date_from = fields.Date('From')
    date_to = fields.Date('To')

    @api.multi
    def print_report_xlsx(self):
        data = {'date_from': self.date_from,
                'date_to': self.date_to,
                'wiz_id': self.id}
        return self.env.ref('odx_scrap_orders.scrap_report_xlsx').report_action(self, data=data)


    @api.multi
    def print_report_pdf(self):
        date_to = str(self.date_to) + ' ' + '23:59:59'
        date_from = str(self.date_from) + ' ' + '00:00:00'

        scrap_orders = self.env['stock.scrap'].search(
            [('create_date', '<=', date_to), ('create_date', '>=', date_from)])
        return self.env.ref('odx_scrap_orders.scarp_order_report').report_action(scrap_orders)


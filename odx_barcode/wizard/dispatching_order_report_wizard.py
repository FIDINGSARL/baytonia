import base64
from datetime import datetime, date, timedelta
from io import BytesIO
from dateutil.relativedelta import relativedelta
from dateutil import parser
from odoo import models, fields, api
import xlwt
import logging

_logger = logging.getLogger(__name__)


class DispatchingOrder(models.TransientModel):
    _name = "dispatching.order.report"

    @api.model
    def _default_from_date(self):
        return date.today() - timedelta(days=7)

    to_date = fields.Date(string="To Date", default=date.today(), required=True)
    from_date = fields.Date(string="From Date", default=_default_from_date, required=True)

    @api.multi
    def generate_dispaching_barcode_report(self):
        print('insideee')
        data = {
            'date_to': self.to_date,
            'wiz_id': self.id}
        return self.env.ref('odx_barcode.date_batch_report_xlsx').report_action(self, data=data)


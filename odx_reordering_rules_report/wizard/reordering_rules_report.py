import base64
from datetime import datetime, date, timedelta
from io import BytesIO
from dateutil.relativedelta import relativedelta
from dateutil import parser
from odoo import models, fields, api
import xlwt
import logging

_logger = logging.getLogger(__name__)


class ReorderingRuleReport(models.TransientModel):
    _name = "reordering.rule.report"

    file_name = fields.Char(string="File Name")
    data = fields.Binary(string="Data")
    to_date = fields.Date(string="To Date", default=date.today(), required=True)
    vendor_ids = fields.Many2many(comodel_name="res.partner", string="Vendors")

    @api.multi
    def generate_stock_product_report(self):
        data = {
            'date_to': self.to_date,
            'wiz_id': self.id}
        return self.env.ref('odx_reordering_rules_report.reordering_rule_report_xlsx').report_action(self, data=data)


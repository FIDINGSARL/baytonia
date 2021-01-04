from odoo import api, models,fields,_
from datetime import datetime,timedelta
import time
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from odoo.api import Environment


class SaleOrder(models.Model):
    _inherit = "sale.order"

    waiting_time = fields.Char(compute='compute_waiting_time', string='Sale Confirm Delay', readonly=True)
    # waiting_time_delivery = fields.Char(compute='compute_waiting_time_delivery', string='Delivery Confirm Delay', readonly=True)


    @api.depends('state')
    def compute_waiting_time(self):
        records = self.env['sale.order'].search([('state', '=', 'sale')])
        for record in records:
            if record.confirmation_date and record.date_order:
                confirm_date=datetime.strptime(record.confirmation_date, "%Y-%m-%d %H:%M:%S")
                order_date = datetime.strptime(record.date_order, "%Y-%m-%d %H:%M:%S")
                record.waiting_time=confirm_date-order_date

    @api.depends('picking_ids.state')
    def compute_waiting_time_delivery(self):
        for record in self:
            for item in record.picking_ids:
                if item.waiting_time:
                    record.waiting_time_delivery = item.waiting_time


class StockPicking(models.Model):
    _inherit = "stock.picking"

    waiting_time = fields.Char(string='Delivery Time Delay', readonly=True)

    @api.multi
    def button_validate(self):
        res= super(StockPicking, self).button_validate()
        if self.create_date:
            date_now = str(datetime.now().replace(microsecond=0))
            current_time = datetime.strptime(date_now, "%Y-%m-%d %H:%M:%S")
            create_date = datetime.strptime(self.create_date, "%Y-%m-%d %H:%M:%S")
            time= current_time - create_date
            self.waiting_time=time
        return res
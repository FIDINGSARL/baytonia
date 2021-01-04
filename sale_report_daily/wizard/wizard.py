from odoo import models, fields, api,_
from datetime import date

class Wizard(models.TransientModel):
    _name = 'sale.report.wizard'

    typesel = fields.Selection([
        ('daily', 'Daily Report'),
        ('monthly', 'Monthly Report'),
        ('yearly', 'Yearly Report')],  string='Required Report',  default='daily')


    @api.multi
    def button_print(self):

       selection = {
            'dat': self.typesel
        }
       # d=self.env.ref('sale_report_daily.report_actions').

       return self.env.ref('sale_report_daily.report_actions').report_action([], data=selection)


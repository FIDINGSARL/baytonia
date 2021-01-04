
from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = "stock.picking"
    
    
    def print_invoice(self):
        if self.invoice_id:
            return self.invoice_id.invoice_print()

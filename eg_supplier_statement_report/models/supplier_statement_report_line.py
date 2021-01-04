from odoo import models, fields


class SupplierStatementReportLine(models.TransientModel):
    _name = 'supplier.statement.report.line'

    serial_no = fields.Integer(string="No.")
    vendor_id = fields.Many2one('res.partner', string="Vendor Name")
    total_cost_purchase = fields.Float('Total Cost Purchase')
    net_invoice_amount = fields.Float('Net Invoice Amount')
    cogs = fields.Float('COGS')
    total_amount_trasfred = fields.Float('Total Amount Transferred')
    total_dept = fields.Float('EOP Debt')
    total_stock = fields.Integer("EOP stock")
    cost_of_current_stock = fields.Float('Cost of Current Stock')
    total_sales = fields.Float("Total Sales")

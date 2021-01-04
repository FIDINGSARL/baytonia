from odoo import api, models


class StockReport(models.AbstractModel):
    _name = 'report.stock.report_picking'

    @api.multi
    def get_report_values(self, docids, data=None):
        docs = self.env['stock.picking'].search([('id', 'in', docids)])
        for doc in docs:
            doc.update({'report_version_number': doc.report_version_number + 1})
        return {
            'docs': docs
        }

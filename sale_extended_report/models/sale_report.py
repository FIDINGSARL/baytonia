from odoo import models,fields,api


class SaleReport(models.Model):
    _inherit = 'sale.report'

    vendor_id = fields.Many2one('res.partner', string='Vendor')

    def _select(self):
        return super(SaleReport, self)._select() + ", l.vendor_id  AS vendor_id"

    def _group_by(self):
        return  super(SaleReport,self)._group_by() + ", l.vendor_id"

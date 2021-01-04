from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    report_version_number = fields.Integer('Version Number',default=0)
    report_version_number_rfq = fields.Integer('Version Number',default=0)


    def update_version_number(self):
        self.report_version_number = self.report_version_number + 1

        return self.report_version_number

    def update_version_number_rfq(self):
        self.report_version_number_rfq = self.report_version_number_rfq + 1

        return self.report_version_number_rfq


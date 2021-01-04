from datetime import date, timedelta

from odoo import models, fields, api


class ImportSaleOrderWizard(models.TransientModel):
    _name = "import.sale.order.wizard"

    @api.model
    def _default_from_date(self):
        return date.today() - timedelta(days=7)

    # timedelta use for substract days

    to_date = fields.Date(string="To Date", default=date.today(), required=True)
    from_date = fields.Date(string="From Date", default=_default_from_date, required=True)

    @api.multi
    def import_sale_order(self):
        self.env["sale.order"].get_remaining_order(from_date=self.from_date, to_date=self.to_date)

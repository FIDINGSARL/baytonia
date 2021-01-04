import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def check_delivery_status_all(self):
        self.check_delivery_status_bulk_vaal()
        self.check_delivery_status_bulk_fl()

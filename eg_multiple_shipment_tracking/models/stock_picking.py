import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = "stock.picking"

    delivery_tracking_lines_ids = fields.One2many('delivery.tracking.line', 'picking_id', string="Tracking Lines")

    def send_to_shipper(self):
        res = super(StockPicking, self).send_to_shipper()
        for tracking_ref in self.carrier_tracking_ref.split(","):
            self.write({'delivery_tracking_lines_ids': [
                (0, 0, {'carrier_id': self.carrier_id.id,
                        'tracking_ref': tracking_ref})]})
        return res

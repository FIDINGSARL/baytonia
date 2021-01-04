import logging

from odoo import fields, models
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)


class DeliveryTrackingLine(models.Model):
    _name = "delivery.tracking.line"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "picking_id"
    _description = 'Delivery Tracking'

    carrier_id = fields.Many2one('delivery.carrier', string="Carrier", track_visibility='onchange')
    tracking_ref = fields.Char(string="Tracking Reference", track_visibility='onchange')
    status_id = fields.Many2one('delivery.carrier.status', string="Status", readonly=True, copy=False,
                                track_visibility='onchange')
    picking_id = fields.Many2one('stock.picking', string="picking", track_visibility='onchange')
    is_return = fields.Boolean('Is Return?')
    sale_id = fields.Many2one(related="picking_id.sale_id")
    purchase_id = fields.Many2one(related="picking_id.move_lines.purchase_line_id.order_id")
    delivery_type = fields.Selection(related="carrier_id.delivery_type")

    def open_website_url(self):
        tracking = self.picking_id.open_website_url()
        return tracking

    def check_delivery_status(self):
        for rec in self:
            if not rec.status_id.is_last_status:
                try:
                    if hasattr(rec, '%s_check_delivery_status' % rec.carrier_id.delivery_type):
                        state = getattr(rec, '%s_check_delivery_status' % rec.carrier_id.delivery_type)()
                        if state:
                            status_ids = self.env['delivery.carrier.status'].search([('name', '=', state)])
                            _logger.info(["=======Status_ids", status_ids])
                            if len(status_ids) == 1:
                                rec.status_id = status_ids.id
                            elif len(status_ids) > 1:
                                _logger.info(
                                    ["=============== Multiple Delivery status found===============", "Picking_id",
                                     rec.id,
                                     "Status name", status_ids.mapped('name')])
                            else:
                                status_id = status_ids.create({'name': state})
                                rec.status_id = status_id.id
                        else:
                            _logger.info(["####### State not found ============ ERROR==========="])
                except Exception as e:
                    _logger.info("===Status fetch error=== {}".format(e))
            else:
                _logger.info(["####### Last Status exist ========== {}     tracking {}============".format(
                    rec.carrier_id.name, rec.tracking_ref)])

    def get_delivery_tracking_line(self, days=20):
        back_date = datetime.today() - timedelta(days=20)
        back_date_str = back_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        tracking_line_ids = self.search([('create_date', '>=', back_date_str)])
        tracking_line_ids.check_delivery_status()

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, timedelta, datetime


class TrackingBarcode(models.Model):
    _name = 'tracking.barcode'
    _inherit = ['barcodes.barcode_events_mixin']
    _description = 'Tracking Barcode'
    _order = 'id desc'

    name = fields.Char(string="Tracking Ref", related='delivery_tracking_line_id.tracking_ref')
    picking_id = fields.Many2one(comodel_name='stock.picking', string='Shipment No',
                                 related='delivery_tracking_line_id.picking_id')
    shipping_company_id = fields.Many2one('delivery.carrier', 'Shipping Company',
                                          related='delivery_tracking_line_id.carrier_id')
    barcode_line_ids = fields.One2many(comodel_name='tracking.barcode.line', inverse_name='barcode_id')
    dispaching_date = fields.Date('Dispaching Date', default=date.today())
    boxes = fields.Integer('No.Boxes', related='picking_id.boxes')
    dispatched_user_id = fields.Many2one('res.users', 'Dispatched By', default=lambda self: self.env.user)
    status_id = fields.Many2one('delivery.carrier.status', 'Status', related='delivery_tracking_line_id.status_id')
    delivery_tracking_line_id = fields.Many2one('delivery.tracking.line', 'Tracking', required=1)
    create_barcode_id = fields.Many2one('create.tracking.barcode','Create Barcode')



    @api.model
    def create(self, vals):
        res = super(TrackingBarcode, self).create(vals)
        if vals.get("delivery_tracking_line_id"):
            tracking = self.env['delivery.tracking.line'].search(
                [('id', '=', int(vals.get("delivery_tracking_line_id")))], limit=1)
            tracking.status_id = self.env.ref('odx_barcode.in_transit_tracking_status')
        return res

    def update_status(self):
        if self.delivery_tracking_line_id:
            self.delivery_tracking_line_id.status_id = self.env.ref('odx_barcode.in_transit_tracking_status')
        if self.shipping_company_id:
            if self.shipping_company_id.delivery_type == 'eg_custom_deliver':
                if self.picking_id:
                    if self.picking_id.sale_id:
                        self.picking_id.sale_id.delivery_status_eg = "In Transit"

    def on_barcode_scanned(self, barcode):
        tracking = self.env['delivery.tracking.line'].search([('tracking_ref', 'ilike', barcode)], limit=1)
        barcode_lines = []
        if tracking:
            self.delivery_tracking_line_id = tracking.id
            if tracking.picking_id:
                for stock_move_id in tracking.picking_id.move_lines:
                    line_dict = {
                        'product_id': stock_move_id.product_id.id,
                        'product_uom_qty': stock_move_id.product_uom_qty,
                        'reserved_availability': stock_move_id.reserved_availability,
                        'quantity_done': stock_move_id.quantity_done,
                        'move_id': stock_move_id.id,
                    }
                    barcode_lines.append((0, 0, line_dict))
                self.barcode_line_ids = barcode_lines
        else:
            raise UserError(
                _('This barcode %s is not related to any record.') %
                barcode)

    def next_state(self):
        action = self.env.ref('odx_barcode.action_tracking_barcode_next').read()[0]
        return action

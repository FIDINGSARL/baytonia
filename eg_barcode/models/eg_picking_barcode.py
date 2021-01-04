from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class PickingBarcode(models.Model):
    _name = 'picking.barcode'
    _inherit = ['barcodes.barcode_events_mixin', 'mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Eg Picking Barcode'
    _rec_name = 'picking_id'

    _sql_constraints = [
        ('picking_id_unique', 'unique (picking_id)', 'The picking must be unique  !')
    ]

    picking_id = fields.Many2one(comodel_name='stock.picking', string='Pickings', ondelete='cascade')
    backorder_id = fields.Many2one(related="picking_id.backorder_id")
    barcode_line_ids = fields.One2many(comodel_name='picking.barcode.line', inverse_name='barcode_id')
    state = fields.Selection(
        [('new', 'New'), ('open', 'Open'), ('validate', 'Validate'), ('done', 'Done'),
         ('cancel', 'Cancel')],
        string='State', default='new')
    message_ids = fields.One2many(related='picking_id.message_ids')
    activity_ids = fields.One2many(related='picking_id.activity_ids')
    message_follower_ids = fields.One2many(related='picking_id.message_follower_ids')
    delivery_tracking_lines_ids = fields.One2many(related='picking_id.delivery_tracking_lines_ids')

    @api.multi
    def get_barcode_lines(self):
        if self.state != "open":
            self.state = "open"
        for stock_move_id in self.picking_id.move_lines:
            move_exist = self.env['picking.barcode.line'].search(
                ['|', ('move_id', '=', stock_move_id.id), ('product_id', '=', stock_move_id.product_id.id),
                 ('barcode_id', '=', self.id)])
            if not move_exist:
                check_auto_populate_done_qty = self.env['ir.config_parameter'].sudo().get_param(
                    'eg_barcode.auto_populated_done_qty')

                self.env['picking.barcode.line'].create({
                    'barcode_id': self.id,
                    'product_id': stock_move_id.product_id.id,
                    'product_uom_qty': stock_move_id.product_uom_qty,
                    'reserved_availability': stock_move_id.reserved_availability,
                    'quantity_done': stock_move_id.reserved_availability if check_auto_populate_done_qty else 0,
                    'move_id': stock_move_id.id,
                })
        return

    def on_barcode_scanned(self, barcode):
        product = self.env['product.product'].search(['|', ('barcode', '=', barcode), ('default_code', '=', barcode)])
        if product:
            barcodeLineObjs = self.barcode_line_ids.filtered(lambda r: r.product_id == product)
            if barcodeLineObjs:
                for barcodeLineObj in barcodeLineObjs:
                    if barcodeLineObj.quantity_done < barcodeLineObj.product_uom_qty:
                        barcodeLineObj.quantity_done += 1
                        break
                    elif barcodeLineObj == barcodeLineObjs[-1]:
                        raise UserError(
                            _('You are trying to deliver quantity more than ordered.'))
            else:
                raise UserError(
                    _('This product %s with barcode %s is not present in this picking.') %
                    (product.name, barcode))
        else:
            raise UserError(
                _('This barcode %s is not related to any product.') %
                barcode)

    def get_scanned_barcode_details(self):
        for line_id in self.barcode_line_ids:
            if line_id.product_uom_qty > line_id.quantity_done:
                self.on_barcode_scanned(line_id.product_id.barcode)
                return
        raise ValidationError("All processed already")

    @api.multi
    def update_done_quantity(self):
        if self.picking_id.state not in ('done', 'draft'):
            for barcode_line_id in self.barcode_line_ids:
                # if barcode_line_id.quantity_done > barcode_line_id.reserved_availability:
                #     raise ValidationError("Done quantity must not be greater than Reserve quantity!!!")
                # else:
                barcode_line_id.move_id.quantity_done = barcode_line_id.quantity_done
                self.state = 'proceed'
        elif self.picking_id.state == 'done':
            self.state = 'done'
        else:
            raise ValidationError("Picking state is not in draft state.!!!")

    def validate_picking(self):
        return self.picking_id.button_validate()

    def change_done_picking_state(self):
        self.state = 'done'

    def check_available_stock(self):
        self.picking_id.action_assign()
        # self.get_barcode_lines()

    def action_cancel(self):
        self.picking_id.action_cancel()

    @api.multi
    def do_print_picking(self):
        return self.picking_id.do_print_picking()

    def send_to_shipper(self):
        if self.picking_id.sale_id.eg_magento_payment_method_id and \
                self.picking_id.sale_id.eg_magento_payment_method_id.code in ["cod", "COD"]:
            if not self.picking_id.invoice_id:
                raise ValidationError("With COD order invoice is must")
        action = self.env.ref('eg_send_to_shipper.wizard_action_wizard_send_to_shipper').read()[0]
        ctx = dict(self._context)
        ctx.update({'active_id': self.picking_id.id, 'active_ids': [self.picking_id.id]})
        action['context'] = ctx
        return action
        # return self.picking_id.with_context(manual=True, active_id=self.picking_id.id).send_to_shipper()

        # def action_report_delivery(self):
    #     print('self',self)
    #     return self.picking_id.action_report_delivery()

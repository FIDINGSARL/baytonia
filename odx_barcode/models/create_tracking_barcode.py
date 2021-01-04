from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, timedelta, datetime
import base64


class CreateTrackingBarcode(models.Model):
    _name = 'create.tracking.barcode'
    _inherit = ['barcodes.barcode_events_mixin']
    _description = 'Create Tracking Barcode'

    boxes = fields.Integer('No.Boxes', related='picking_id.boxes')
    scaned_boxes = fields.Integer('Scanned Boxes', related='scanned_boxes_copy')
    scanned_boxes_copy = fields.Integer('Scanned Boxes Copy')
    name = fields.Char('Name', readonly=True)
    picking_id = fields.Many2one(comodel_name='stock.picking', string='Shipment No',
                                 related='delivery_tracking_line_id.picking_id')
    delivery_tracking_line_id = fields.Many2one('delivery.tracking.line', 'Tracking')
    tracking_barcode_ids = fields.One2many('tracking.barcode', 'create_barcode_id', string='Tracking Barcode',
                                           store=True)
    state = fields.Selection([('draft', 'Draft'), ('start', 'Start'), ('finish', 'Finish')], string='Status',
                             readonly=True,
                             default='draft')
    dispatched_user_id = fields.Many2one('res.users', 'Dispatched By', default=lambda self: self.env.user)
    shipping_company_id = fields.Many2one('delivery.carrier', 'Shipping Company',
                                          related='delivery_tracking_line_id.carrier_id')
    end_date = fields.Datetime('End Date')
    start_date = fields.Datetime('start Date')
    dispaching_date = fields.Date('Dispaching Date', default=date.today())

    # time_stamp = fields.Char('Time stamp', compute='compute_time_stamp')
    #
    # @api.depends('end_date', 'start_date')
    # def compute_time_stamp(self):
    #     for rec in self:
    #         if rec.start_date and rec.end_date:
    #             print(parser.parse(rec.end_date) - parser.parse(rec.start_date))
    #             rec.time_stamp = (parser.parse(rec.end_date) - parser.parse(rec.start_date))
    #     print('aaaaaaa')

    @api.model
    def create(self, values):
        seq = self.env['ir.sequence'].next_by_code('create.tracking.barcode') or '/'
        values['name'] = seq
        return super(CreateTrackingBarcode, self.sudo()).create(values)

    @api.multi
    def dispatching_report(self):

        today = str(date.today())

        pdf = self.env.ref('odx_barcode.dispatching_report').render_qweb_pdf(self.ids)
        b64_pdf = base64.b64encode(pdf[0])

        ATTACHMENT_NAME = "Dispatching Order"
        attachment_id = self.env['ir.attachment'].create({
            'name': ATTACHMENT_NAME,
            'type': 'binary',
            'datas': b64_pdf,
            'datas_fname': ATTACHMENT_NAME + '.pdf',
            'store_fname': ATTACHMENT_NAME,
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/x-pdf'
        })

        ir_model_data = self.env['ir.model.data']

        try:
            template_id = \
                ir_model_data.get_object_reference('odx_barcode', 'email_template_dispatching_order')[
                    1]
        except ValueError:
            template_id = False
        ctx = {
            'default_model': None,
            'default_res_id': None,
            'default_use_template': True,
            'default_template_id': self.env.ref('odx_barcode.email_template_dispatching_order'),
            'default_composition_mode': 'comment',
            'web_base_url': self.env['ir.config_parameter'].get_param('web.base.url'),
            'mark_so_as_sent': True,
            # 'custom_layout': "sale.mail_template_data_notification_email_sale_order",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True
        }
        template = self.env['mail.template'].browse(template_id)
        html_body = template.body_html
        # for email_recipients in email_to:
        compose = self.env['mail.mail'].with_context(ctx).create({
            'subject': 'Dispatching Order : ' + today,
            'body_html': html_body,
            'email_to': template.email_to,
            'email_cc': template.email_to,
            'attachment_ids': [(6, 0, [attachment_id.id])] or None,

        })
        compose.send()

        return self.env.ref('odx_barcode.dispatching_report').report_action(self)

    def on_barcode_scanned(self, barcode):
        if not self.env.user.has_group('odx_barcode.group_dispatching_barcode'):
            raise UserError(
                _("You don't  have  accces to scan barcode"))
        if self.state == 'draft':
            raise UserError(
                _("Please Click Start Button"))
        if self.state == 'finish':
            raise UserError(
                _("The Session Is Completed"))

        tracking = self.env['delivery.tracking.line'].search([('tracking_ref', 'ilike', barcode)], limit=1)
        barcode_lines = []
        if tracking:
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
            tracking_barcode = self.env['tracking.barcode'].create({'delivery_tracking_line_id': tracking.id,
                                                                    'barcode_line_ids': barcode_lines,
                                                                    })
            self.picking_id = tracking.picking_id
            self.delivery_tracking_line_id = tracking.id
            # self.update({
            #     'tracking_barcode_ids': [(0, 0, {'delivery_tracking_line_id': tracking.id,
            #                                      'barcode_line_ids': barcode_lines,
            #                                      })]
            # })
            # self.boxes = tracking.picking_id.boxes if tracking.picking_id else 0
            # scanned_boxes = self.scaned_boxes + 1
            # self.scanned_boxes_copy = scanned_boxes
        else:
            raise UserError(
                _('This barcode %s is not related to any record.') %
                barcode)

    def submit(self):
        # if self.boxes > self.scaned_boxes:
        #     raise UserError(
        #         _('Only Scanned %s Boxes,The Order Contain %s Boxes') %
        #         (self.scaned_boxes, self.boxes))
        # if self.boxes < self.scaned_boxes:
        #     raise UserError(
        #         _('You Scanned %s Boxes,The Order Contain Only %s Boxes') %
        #         (self.scaned_boxes, self.boxes))
        tracking_barcodes = self.env['tracking.barcode'].search([('picking_id', '=', self.picking_id.id)])
        for barcode in tracking_barcodes:
            barcode.update_status()
            # barcode.create_barcode_id = self.id

        # self.scaned_boxes =0
        # self.unlink()
        # action = self.env.ref('odx_barcode.action_create_tracking_barcode').read()[0]
        # return action

    def finish(self):
        self.update({
            'state': 'finish',
            'end_date': datetime.today()
        })

        tracking_barcodes = self.env['tracking.barcode'].search(
            [('create_date', '<=', str(self.end_date)), ('create_date', '>=', str(self.start_date))])
        for barcode in tracking_barcodes:
            barcode.update_status()
            barcode.create_barcode_id = self.id

    def start(self):
        self.update({
            'state': 'start',
            'start_date': datetime.today(),
            'dispatched_user_id': self.env.user.id
        })

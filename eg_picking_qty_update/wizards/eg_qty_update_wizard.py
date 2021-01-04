from odoo import fields, models, api
from odoo.exceptions import ValidationError


class EgQtyUpdateWizard(models.TransientModel):
    _name = 'eg.qty.update.wizard'
    _description = 'Stock Picking Wizard'

    @api.model
    def default_get(self, fields_list):
        record = super(EgQtyUpdateWizard, self).default_get(fields_list)
        stock_picking_active_id = self.env['stock.picking'].browse(self._context['active_id'])

        if 'wizard_line_ids' in fields_list:
            lines = []
            for stock_move_id in stock_picking_active_id.move_lines:
                lines.append({
                    'product_id': stock_move_id.product_id.id,
                    'product_uom_qty': stock_move_id.product_uom_qty,
                    'reserved_availability': stock_move_id.reserved_availability,
                    'quantity_done': stock_move_id.reserved_availability,
                    'move_id': stock_move_id.id,
                })
                record['wizard_line_ids'] = [(0, 0, x) for x in lines]
        return record

    wizard_line_ids = fields.One2many(comodel_name='eg.qty.update.wizard.line', inverse_name='wizard_id')

    @api.multi
    def update_quantity_done(self):
        active_stock_picking_id = self.env['stock.picking'].browse(self._context['active_id'])
        active_stock_picking_id.update_process = True
        if active_stock_picking_id.state != 'done':
            for wizard_line_id in self.wizard_line_ids:
                wizard_line_id.move_id.quantity_done = wizard_line_id.quantity_done

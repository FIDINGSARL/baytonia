from odoo import fields, models, api
from odoo.exceptions import ValidationError


class QtyUpdateWizard(models.TransientModel):
    _name = 'qty.update.wizard'
    _description = 'Purchase Order Wizard'

    @api.model
    def default_get(self, fields_list):
        record = super(QtyUpdateWizard, self).default_get(fields_list)
        purchase_order_id = self.env['purchase.order'].browse(self._context['active_id'])

        if 'wizard_line_ids' in fields_list:
            lines = []
            for order_line_id in purchase_order_id.order_line:
                lines.append({
                    'product_id': order_line_id.product_id.id,
                    'product_qty': order_line_id.product_qty,
                    'order_line_id': order_line_id.id,
                    'price_unit': order_line_id.price_unit
                })
                record['wizard_line_ids'] = [(0, 0, x) for x in lines]
        return record

    wizard_line_ids = fields.One2many(comodel_name='qty.update.wizard.line', inverse_name='wizard_id')

    @api.multi
    def update_quantity_price(self):
        purchase_order_id = self.env['purchase.order'].browse(self._context['active_id'])
        if purchase_order_id.state in ["draft", "sent", "to approve"]:
            for wizard_line_id in self.wizard_line_ids:
                wizard_line_id.order_line_id.product_qty = wizard_line_id.product_qty
                wizard_line_id.order_line_id.price_unit = wizard_line_id.price_unit

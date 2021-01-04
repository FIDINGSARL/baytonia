from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    sale_order_ids = fields.One2many('sale.order.line', 'vendor_id', string='Order Lines')

    @api.multi
    def sale_order_button(self):
        view1 = self.env.ref('sale.view_order_line_tree')
        return {
            'name': ('Sale Orders'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'sale.order.line',
            'views': [(view1.id, 'tree')],
            'view_id': False,
            'target': 'current',
            'domain': [('vendor_id', '=', self.id)]

        }

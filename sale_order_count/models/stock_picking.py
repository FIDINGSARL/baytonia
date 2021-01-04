from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    sale_order_count = fields.Integer('Previous Sale Orders', compute='compute_so_count')

    @api.depends('partner_id')
    def compute_so_count(self):
        for picking in self:
            count = self.env['sale.order'].search_count([('partner_id', '=', picking.partner_id.id)]) - 1
            if count > 0:
                picking.sale_order_count = count

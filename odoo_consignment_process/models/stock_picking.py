# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    is_consignment = fields.Boolean(
        string='Is Consignment Order',
    )

    @api.multi
    def button_validate(self):
        self.ensure_one()
        res = super(StockPicking, self).button_validate()
        if not self.is_consignment:
            return  res

        for line in self.move_lines:
            if line.purchase_line_id:
                line.product_id.write({
                    'picking_id': self.id
                })
        return res

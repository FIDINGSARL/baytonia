from odoo import models, api, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def default_get(self, fields_list):
        res = super(SaleOrder, self).default_get(fields_list)
        if 'picking_policy' in fields_list:
            res[
                'picking_policy'] = self.env.user.company_id.picking_policy if self.env.user.company_id.picking_policy else \
            res['picking_policy']
        return res

from odoo import api, models


class SynchronizationWizard(models.TransientModel):
    _inherit = 'synchronization.wizard'

    @api.multi
    def start_bulk_product_product_synchronization(self):
        if self.action == 'update':
            ctx = dict(self._context or {})
            product_ids = self.env['product.product'].browse(ctx.get('active_ids'))
            for product in product_ids:
                product.update_odoo_to_magento_price_qty_name()
        else:
            return super(SynchronizationWizard, self).start_bulk_product_product_synchronization()
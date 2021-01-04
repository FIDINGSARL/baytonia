from odoo import api, models


class SynchronizationWizard(models.TransientModel):
    _inherit = 'synchronization.wizard'

    @api.multi
    def start_bulk_product_product_synchronization(self):
        """
        To sync product.template from product.product record
        :return:
        """
        ctx = dict(self._context or {})
        product_ids = self.env['product.product'].browse(ctx.get('active_ids'))
        product_tmpl_ids = product_ids.mapped('product_tmpl_id').ids

        ctx.update(
            sync_opr=self.action,
            active_model='product.template',
            active_ids=product_tmpl_ids,
        )
        message = self.env['magento.synchronization'].with_context(
            ctx).export_product_check()
        return message

    @api.model
    def start_bulk_product_product_synchronization_wizard(self):
        partial = self.create({})
        ctx = dict(self._context or {})
        ctx.update({'product': 'product'})
        return {'name': "Synchronization Bulk Product",
                'view_mode': 'form',
                'view_id': False,
                'view_type': 'form',
                'res_model': 'synchronization.wizard',
                'res_id': partial.id,
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                'context': ctx,
                'domain': '[]',
                }

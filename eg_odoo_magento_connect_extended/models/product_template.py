import logging

from odoo import models, api

_logger = logging.getLogger('===Pro_tmpl===== ')


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def cron_update_product_on_magento(self, limit=150):
        """
        to update product on magento via cron 50 at a time
        :return:
        """
        ctx = dict(self._context or {})
        m_product_template_ids = self.env['magento.product.template'].search([('need_sync', '=', 'Yes')], limit=limit)
        count = len(m_product_template_ids)
        for m_product_template_id in m_product_template_ids:
            _logger.info(["==========Remaining======= ::::: ", count])
            count -= 1
            try:
                ctx.update(
                    sync_opr='update',
                    active_model='product.template',
                    active_ids=m_product_template_id.template_name.ids,
                )
                self.env['magento.synchronization'].with_context(ctx).export_product_check()
                self.env.cr.commit()
            except Exception as e:
                _logger.info(["=========Product Sync Exception====", e])
        return

    @api.model
    def cron_export_product_on_magento(self, limit=150):
        """
        to update product on magento via cron 50 at a time
        :return:
        """
        ctx = dict(self._context or {})
        instance_id = self.env['magento.configure'].search([('active', '=', True)])
        m_product_template_ids = self.env['magento.product.template'].search([])
        synced_tmpl_ids = m_product_template_ids.mapped('template_name').ids
        product_tmpl_ids = self.env['product.template'].search(
            [('id', 'not in', synced_tmpl_ids), ('type', '!=', 'service')], limit=limit)
        count = len(product_tmpl_ids)
        for product_template_id in product_tmpl_ids:
            _logger.info(["Remaining Product export======= ||| ", count])
            _logger.info(["Syncing Product id======= ||| ", product_template_id])
            count -= 1
            try:
                ctx.update(
                    sync_opr='export',
                    active_model='product.template',
                    active_ids=product_template_id.ids,
                )
                self.env['magento.synchronization'].with_context(ctx).export_product_check()
                self.env.cr.commit()
            except Exception as e:
                _logger.info([" Exception====||| ", e])
        return

    @api.model
    def create(self, vals):
        _logger.info(["Create", vals])
        res = super(ProductTemplate, self).create(vals)
        ctx = dict(self._context or {})
        if 'magento' in ctx:
            res.type = "product"
        return res

    @api.multi
    def write(self, vals):
        _logger.info(["Write", vals])
        res = super(ProductTemplate, self).write(vals)
        ctx = dict(self._context or {})
        if 'magento' in ctx:
            for rec in self:
                if rec.type != 'product':
                    rec.write({'type': 'product'})
        return res

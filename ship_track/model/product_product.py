from odoo import models,fields,api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    @api.depends('seller_ids.name')
    def _get_vendor(self):
        for product in self:
            if product.seller_ids:
                product.vendor_id = product.seller_ids[0].name.id

    vendor_id = fields.Many2one('res.partner', string='Vendor', compute='_get_vendor', store= True)
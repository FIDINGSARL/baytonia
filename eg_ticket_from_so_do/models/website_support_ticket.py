import logging

from odoo import fields, models, api

_logging = logging.getLogger(__name__)


class WebsiteSupportTicket(models.Model):
    _inherit = 'website.support.ticket'

    sale_order_id = fields.Many2one(comodel_name='sale.order', string='Sale Order')
    stock_picking_id = fields.Many2one(comodel_name='stock.picking')
    eg_magento_payment_method_id = fields.Many2one("magento.payment.method", "M Payment Method",
                                                   compute="_compute_payment_method_id", store=True)
    partner_ids = fields.Many2many(related="stock_picking_id.partner_ids")

    @api.depends('sale_order_id', 'stock_picking_id')
    @api.multi
    def _compute_payment_method_id(self):
        for rec in self:
            if rec.sale_order_id and rec.sale_order_id.eg_magento_payment_method_id:
                rec.eg_magento_payment_method_id = rec.sale_order_id.eg_magento_payment_method_id.id
            elif rec.stock_picking_id and rec.stock_picking_id.eg_magento_payment_method_id:
                rec.eg_magento_payment_method_id = rec.stock_picking_id.eg_magento_payment_method_id.id

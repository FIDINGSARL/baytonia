import logging

from odoo import models, fields, api, tools

_logger = logging.getLogger(__name__)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    # @api.depends('product_id')
    # def set_image(self):
    #     woo_product_obj = self.env['woo.product.product.ept']
    #
    #     for move in self:
    #         if move.product_id:
    #             woo_products = woo_product_obj.search([('product_id', '=', move.product_id.id)], limit=1)
    #             if woo_products:
    #                 for image in woo_products.woo_template_id.woo_gallery_image_ids:
    #                     if image.url_image_id:
    #                         try:
    #                             resized_images = tools.image_get_resized_images(image.url_image_id, return_big=True,
    #                                                                             avoid_resize_medium=True)
    #                             move.image_small = resized_images['image_small']
    #                         except:
    #                             pass

    image_small = fields.Binary('Product Image')

    @api.model
    def create(self, vals):
        res = super(PurchaseOrderLine, self).create(vals)
        if res.product_id.image_small:
            res.image_small = res.product_id.image_small
            # woo_product_obj = self.env['woo.product.product.ept']
            # woo_products = woo_product_obj.search([('product_id', '=', res.product_id.id)], limit=1)
            # if woo_products:
            #     for image in woo_products.woo_template_id.woo_gallery_image_ids:
            #         if image.url_image_id:
            #             try:
            #                 resized_images = tools.image_get_resized_images(image.url_image_id, return_big=True,
            #                                                                 avoid_resize_medium=True)
            #                 res.image_small = resized_images['image_small']
            #                 break
            #             except Exception as e:
            #                 _logger.info(e)
        return res


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    credit_note_status = fields.Boolean('Is Credit Note', store=True, compute="_compute_credit_note_status")

    @api.depends('order_line.invoice_lines.invoice_id')
    def _compute_credit_note_status(self):

        for order in self:
            invoices = self.env['account.invoice']
            for line in order.order_line:
                invoices |= line.invoice_lines.mapped('invoice_id')
            for invoice in invoices:
                if invoice.type in ['in_refund']:
                    order.credit_note_status = True

    @api.multi
    def update_image(self):
        # woo_product_obj = self.env['woo.product.product.ept']
        for purchase_id in self:
            for line in purchase_id.order_line:
                line.image_small = line.product_id.image_small
                # if line.product_id:
                #     woo_products = woo_product_obj.search([('product_id', '=', line.product_id.id)], limit=1)
                #     if woo_products:
                #         for image in woo_products.woo_template_id.woo_gallery_image_ids:
                #             resized_images = tools.image_get_resized_images(image.url_image_id, return_big=True,
                #                                                             avoid_resize_medium=True)
                #             line.image_small = resized_images['image_small']
                #             break

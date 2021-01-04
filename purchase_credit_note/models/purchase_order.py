from odoo import models, fields, api, tools


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    credit_note_eg = fields.Float('Credit Note', compute="_compute_credit_note_eg", store=True)

    @api.depends('invoice_ids')
    def _compute_credit_note_eg(self):
        for rec in self:
            credit_note_ids = rec.invoice_ids.filtered(lambda i: i.type == 'in_refund')
            rec.credit_note_eg = sum(credit_note_ids.mapped('amount_total'))


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
    #
    # image_small = fields.Binary('Product Image', compute=set_image)

    @api.onchange('product_id')
    def onchange_product_id_eg(self):
        self.price_unit = self.product_id.standard_price

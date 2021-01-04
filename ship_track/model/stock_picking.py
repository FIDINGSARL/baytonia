import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class StockPick(models.Model):
    _inherit = 'stock.picking'

    @api.depends('state', 'sale_id', 'sale_id.amount_total')
    def _get_total_amount(self):
        for picking in self:
            if picking.sale_id:
                picking.total_amount = picking.sale_id.amount_total

    ship_track = fields.Char(string="Ship Tracking Number")
    # payment_gateway_id = fields.Many2one("woo.payment.gateway", "Payment Gateway")
    total_amount = fields.Float('Total Amount', compute=_get_total_amount, store=True)
    partner_city = fields.Char('Destination City', related='partner_id.city')

    # @api.multi
    # def button_validate(self):
    #
    #     if self.sale_id:
    #         self.sale_id.ship_track = self.ship_track
    #
    #     return super(StockPick, self).button_validate()

    @api.multi
    def update_image(self):
        for picking_id in self:
            for move in picking_id.move_lines:
                move.image_small = move.product_id.image_small
                # if move.product_id:
                #     woo_products = woo_product_obj.search([('product_id', '=', move.product_id.id)], limit=1)
                #     if woo_products:
                #         for image in woo_products.woo_template_id.woo_gallery_image_ids:
                #             resized_images = tools.image_get_resized_images(image.url_image_id, return_big=True,
                #                                                             avoid_resize_medium=True)
                #             move.image_small = resized_images['image_small']
                #             break


# This is not required as it is duplicating delivery label by sending twice to API, remove by Sahil Navadiya
#     @api.multi
#     def send_to_shipper(self):
#         res =  super(StockPick, self).send_to_shipper()
#         self.ensure_one()
#         res = self.carrier_id.send_shipping(self)[0]
#         if self.carrier_id.free_over and self.sale_id and self.sale_id._compute_amount_total_without_delivery() >= self.carrier_id.amount:
#             res['exact_price'] = 0.0
#         self.carrier_price = res['exact_price']
#         if res['tracking_number']:
#             self.carrier_tracking_ref = res['tracking_number']
#         order_currency = self.sale_id.currency_id or self.company_id.currency_id
#         msg = _("Shipment sent to carrier %s for shipping with tracking number %s<br/>Cost: %.2f %s") % (
#         self.carrier_id.name, self.carrier_tracking_ref, self.carrier_price, order_currency.name)
#         self.sale_id.message_post(body=msg)


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def _get_sale_line_total(self):
        for move in self:
            move.sale_price = move.sale_line_id.price_total

    # @api.depends('product_id')
    # def set_image(self):
    #     woo_product_obj = self.env['woo.product.product.ept']
    #     for move in self:
    #         if move.product_id:
    #             woo_products = woo_product_obj.search([('product_id', '=', move.product_id.id)], limit=1)
    #             if woo_products:
    #                 for image in woo_products.woo_template_id.woo_gallery_image_ids:
    #                     resized_images = tools.image_get_resized_images(image.url_image_id, return_big=True,
    #                                                                     avoid_resize_medium=True)
    #                     move.image_small = resized_images['image_small']

    sale_price = fields.Float('Sale Total Price', compute='_get_sale_line_total')
    sale_unit_price = fields.Float('Sale Unit Price', related='sale_line_id.price_unit')
    rack = fields.Char(string="Rack", related='product_id.rack', readonly=True)
    image_small = fields.Binary('Product Image')

    @api.model
    def create(self, vals):
        res = super(StockMove, self).create(vals)
        if res.product_id.image_small:
            res.image_small = res.product_id.image_small
            # woo_product_obj = self.env['woo.product.product.ept']
            # woo_products = woo_product_obj.search([('product_id', '=', res.product_id.id)], limit=1)
            # if woo_products:
            #     for image in woo_products.woo_template_id.woo_gallery_image_ids:
            #         try:
            #             resized_images = tools.image_get_resized_images(image.url_image_id, return_big=True,
            #                                                             avoid_resize_medium=True)
            #             res.image_small = resized_images['image_small']
            #             break
            #         except Exception as e:
            #             _logger.info(e)
        return res

class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    tracking_url = fields.Text(string="Tracking URL")

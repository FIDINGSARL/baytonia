# -*- coding: utf-8 -*-
# Part of eComBucket. See LICENSE file for full copyright and licensing details.
import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

BasicAddress = ['name', 'email', 'phone', 'mobile', 'street', 'street2', 'city', 'zip', 'lang']


class Picking(models.Model):
    _inherit = "stock.picking"
    cod_amount = fields.Float(
        string='COD Amount',
    )


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"
    default_product_weight = fields.Float(
        default=1,
        string='Default  Weight',
        help="Default  weight  will use in  package if product not have weight"
    )

    @api.model
    def _get_default_uom(self):
        uom_categ_id = self.env.ref('product.product_uom_categ_kgm').id
        return self.env['product.uom'].search([('category_id', '=', uom_categ_id), ('factor', '=', 1)], limit=1)

    @api.model
    def _get_item_data(self, order=None, pickings=None, uom_id=None):
        weight, volume, quantity, amount = 0, 0, 0, 0
        items = order.order_line if order else pickings.move_lines
        for line in items:
            if order and line.state == 'cancel':
                continue
            if order and (not line.product_id or line.is_delivery):
                continue
            q = self._get_default_uom()._compute_quantity(
                line.product_uom_qty, uom_id)
            weight += (line.product_id.weight or 0.0) * q
            volume += (line.product_id.volume or 0.0) * q
            amount += (line.product_id.lst_price or 0.0) * q
            quantity += q
        if pickings:
            # amount = pickings.cod_amount

            # order = self.env['sale.order'].search([('name','=',pickings.origin)])
            # invoiced_amount = self.env['account.invoice'].search([('origin','=',pickings.origin)]).mapped('amount_total')
            # if order and order.payment_gateway_id and order.payment_gateway_id.code == 'cod':
            #     amount = order.amount_total - sum(invoiced_amount)

            # Code added by Sahil
            cod_amount = 0.0
            # if pickings.sale_id.payment_gateway_id and pickings.sale_id.payment_gateway_id.code in ["cod", "COD"]:
            #     cod_amount = pickings.sale_id.amount_total
            #
            #     for inv in self.env['account.invoice'].search([('origin', '=', pickings.sale_id.name)]):
            #         if inv.state == "paid":
            #             cod_amount = cod_amount - inv.amount_total
            #         elif inv.state == "open":
            #             if inv.amount_total != inv.residual and inv.residual > 0:
            #                 cod_amount = cod_amount - (inv.amount_total - inv.residual)
            if pickings.sale_id.eg_magento_payment_method_id and pickings.sale_id.eg_magento_payment_method_id.code in [
                "cod", "COD"]:
                cod_amount = pickings.sale_id.amount_total

                for inv in self.env['account.invoice'].search([('origin', '=', pickings.sale_id.name)]):
                    if inv.state == "paid":
                        cod_amount = cod_amount - inv.amount_total
                    elif inv.state == "open":
                        if inv.amount_total != inv.residual and inv.residual > 0:
                            cod_amount = cod_amount - (inv.amount_total - inv.residual)
            # _logger.info("\n\nHEre COd : %s\n",cod_amount)
        return dict(weight=weight, volume=volume, quantity=quantity, amount=cod_amount)

    @api.model
    def get_package_count(self, weight_limit, order=None, pickings=None):
        WeightValue = self._get_weight(
            order=order) if order else self._get_weight(pickings=pickings)
        assert (WeightValue != 0.0), _(
            'Product in Order Must Have Weight For Getting Shipping Charges.')
        last_package = WeightValue % weight_limit
        total_package = int(WeightValue // weight_limit)
        return WeightValue, weight_limit, last_package, total_package + int(bool(last_package))

    def get_shipment_currency_id(self, order=None, pickings=None):
        currency = None  # ,'USD'
        if order:
            currency = order.currency_id
        elif pickings:
            if pickings.sale_id and pickings.sale_id.currency_id:
                currency = pickings.sale_id.currency_id
            else:
                currency = pickings.company_id.currency_id
                if not currency:
                    warehouse = pickings.picking_type_id and pickings.picking_type_id.warehouse_id
                    if warehouse:
                        currency = (warehouse.property_product_pricelist
                                    and warehouse.property_product_pricelist.currency_id)
        if not currency:
            currency = currency or self.env['res.currency'].search(('name', 'in', ['USD', 'EUR']), limit=1)
        return currency

    def get_shipment_currency(self, order=None, pickings=None):
        currency = 'USD'
        if order:
            currency = order.currency_id.name
        elif pickings:
            if pickings.sale_id.currency_id:
                currency = pickings.sale_id.currency_id.name
            else:
                currency = pickings.company_id.currency_id.name
        return currency

    def get_shipment_address(self, entity):

        data = entity.read(BasicAddress)[0]
        company_name = None
        if entity.parent_id:
            company_name = entity.parent_id.name

        data['country_name'] = entity.country_id.name
        data['country_code'] = entity.country_id.code
        data['state_name'] = entity.state_id.name
        data['state_code'] = entity.state_id.code
        data['company_name'] = company_name
        return data

    def get_shipment_recipient_address(self, order=None, picking=None):
        if order:
            recipient = order.partner_shipping_id if order.partner_shipping_id else order.partner_id
        else:
            recipient = picking.partner_id
        if not len(recipient):
            raise ValidationError('Please check partner address.')
        return self.get_shipment_address(recipient)

    def get_shipment_shipper_address(self, order=None, picking=None):
        if order:
            shipper = order.warehouse_id.partner_id
        else:
            shipper = picking.picking_type_id.warehouse_id.partner_id
        if not len(shipper):
            raise ValidationError('Please check warehouse address.')
        return self.get_shipment_address(shipper)

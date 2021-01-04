from odoo import models, api, fields, _
from odoo.addons import decimal_precision as dp

from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.depends('order_line.qty_received', 'order_line.product_qty')
    def _compute_remaining_qty(self):
        for order in self:
            qty_balance  = 0
            for line in order.order_line:
                qty_balance += (line.product_qty - line.qty_received)
            order.quantity_tobe_received = qty_balance

    quantity_tobe_received = fields.Float(compute='_compute_remaining_qty', string="Yet Receive Qty",
                                          digits=dp.get_precision('Product Unit of Measure'), store=True,
                                          compute_sudo=True)



class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    source_doc = fields.Char('Source')

    @api.onchange('product_qty', 'product_uom')
    def _onchange_quantity(self):
        res = super(PurchaseOrderLine, self)._onchange_quantity()
        if not self.price_unit:
            self.price_unit = self.product_id.standard_price
        return res


class ProcurementRule(models.Model):
    _inherit = 'procurement.rule'

    @api.multi
    def _run_buy(self, product_id, product_qty, product_uom, location_id, name, origin, values):
        cache = {}
        suppliers = product_id.seller_ids \
            .filtered(lambda r: (not r.company_id or r.company_id == values['company_id']) and (
                    not r.product_id or r.product_id == product_id))
        if not suppliers:
            msg = _('There is no vendor associated to the product %s. Please define a vendor for this product.') % (
            product_id.display_name,)
            raise UserError(msg)

        supplier = self._make_po_select_supplier(values, suppliers)
        partner = supplier.name

        domain = self._make_po_get_domain(values, partner)

        if domain in cache:
            po = cache[domain]
        else:
            po = self.env['purchase.order'].sudo().search([dom for dom in domain])
            po = po[0] if po else False
            cache[domain] = po
        if not po:
            vals = self._prepare_purchase_order(product_id, product_qty, product_uom, origin, values, partner)
            company_id = values.get('company_id') and values['company_id'].id or self.env.user.company_id.id
            po = self.env['purchase.order'].with_context(force_company=company_id).sudo().create(vals)
            cache[domain] = po
        elif not po.origin or origin not in po.origin.split(', '):
            if po.origin:
                if origin:
                    po.write({'origin': po.origin + ', ' + origin})
                else:
                    po.write({'origin': po.origin})
            else:
                po.write({'origin': origin})

        # Create Line
        po_line = False
        for line in po.order_line:
            if line.product_id == product_id and line.product_uom == product_id.uom_po_id:
                if line._merge_in_existing_line(product_id, product_qty, product_uom, location_id, name, origin,
                                                values):
                    vals = self._update_purchase_order_line(product_id, product_qty, product_uom, values, line, partner)
                    if line.source_doc:
                        if origin:
                            line.write({'source_doc': line.source_doc + ', ' + origin})
                        else:
                            po.write({'source_doc': po.origin})

                    po_line = line.write(vals)
                    break
        if not po_line:
            vals = self._prepare_purchase_order_line(product_id, product_qty, product_uom, values, po, supplier)
            vals['source_doc'] = origin
            self.env['purchase.order.line'].sudo().create(vals)

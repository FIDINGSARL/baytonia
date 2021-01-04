from odoo import fields, models, api


class PickingBarcodeLine(models.Model):
    _name = 'picking.barcode.line'
    _description = 'Eg Picking Barcode Line'

    barcode_id = fields.Many2one(comodel_name='picking.barcode', ondelete='cascade')
    product_id = fields.Many2one(comodel_name='product.product', string="Product")
    picking_barcode_editable = fields.Boolean(related="product_id.picking_barcode_editable", readonly=True, store=True)
    bundle_product = fields.Boolean(string="Bundle Product", compute="_compute_bundle_product")
    product_uom_qty = fields.Float(related="move_id.product_uom_qty")
    reserved_availability = fields.Float(related="move_id.reserved_availability")
    quantity_done = fields.Float(related="move_id.quantity_done")
    move_id = fields.Many2one(comodel_name='stock.move')

    @api.depends("product_id")
    def _compute_bundle_product(self):
        for rec in self:
            if rec.product_id:
                if "طقم" in rec.product_id.name:
                    rec.bundle_product = True
                else:
                    rec.bundle_product = False
            else:
                rec.bundle_product = False

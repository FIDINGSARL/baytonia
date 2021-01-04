from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = "product.product"

    picking_barcode_editable = fields.Boolean(string="Picking Barcode Editable", readonly=True,
                                              compute="_compute_picking_barcode_readonly", store=True)

    @api.depends("route_ids")
    def _compute_picking_barcode_readonly(self):
        mto_mts_id = self.env.ref('stock_mts_mto_rule.route_mto_mts')
        for rec in self:
            if rec.route_ids:
                if mto_mts_id in rec.route_ids:
                    rec.picking_barcode_editable = True
                else:
                    rec.picking_barcode_editable = False

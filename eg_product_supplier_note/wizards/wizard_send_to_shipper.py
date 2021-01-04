from odoo import models, fields, api


class WizardSendToShipper(models.TransientModel):
    _inherit = "wizard.send.to.shipper"

    supplier_ids = fields.Many2many(comodel_name="product.supplierinfo", string="Suppliers")

    @api.model
    def default_get(self, fields_list):
        res = super(WizardSendToShipper, self).default_get(fields_list)

        picking_id = self.env["stock.picking"].browse(self._context.get('active_id'))
        supplier_ids = self.env["product.supplierinfo"]
        for move_line in picking_id.move_lines:
            supplier_ids += move_line.product_id.product_tmpl_id.seller_ids.filtered(
                lambda l: l.note != "" and l.id not in supplier_ids.ids)
        if 'supplier_ids' in fields_list:
            res["supplier_ids"] = supplier_ids.ids
        return res

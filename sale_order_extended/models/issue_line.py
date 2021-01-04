from odoo import models, fields, api
from datetime import datetime, date
import odoo


class IssueLine(models.Model):
    _name = "issue.line"

    reason_id = fields.Many2one(comodel_name="issue.reason", string="Reason")
    order_id = fields.Many2one(comodel_name="sale.order", string="Sale Order")
    sale_line_id = fields.Many2one(comodel_name="sale.order.line", string="Order Line")
    product_id = fields.Many2one(comodel_name="product.product", string="Product")
    order_qty = fields.Float(string="Quantity")
    unit_price = fields.Float(string="Unit Price")
    generate_date = fields.Datetime(string="Generate Date", default=datetime.now())
    responsible_id = fields.Many2one(comodel_name="res.users", string="Responsible Person")
    confirm_person_id = fields.Many2one(comodel_name="res.users", string="Confirm By")
    carrier_id = fields.Many2one(comodel_name="delivery.carrier", string="Shipping Company")
    image_small = fields.Binary('Image')

    @api.onchange("sale_line_id")
    def onchange_sale_line_id(self):
        sale_line_id = self.sale_line_id
        self.product_id = sale_line_id and sale_line_id.product_id.id or None
        self.order_qty = sale_line_id and sale_line_id.product_uom_qty or None
        self.unit_price = sale_line_id and sale_line_id.price_unit or None
        if sale_line_id:
            if self.order_id.picking_ids:
                picking_ids = self.order_id.picking_ids.filtered(
                    lambda l: sale_line_id.product_id in l.move_lines.mapped("product_id"))

                if picking_ids:
                    self.responsible_id = picking_ids[0].responsible_id and picking_ids[0].responsible_id.id or None
                    self.confirm_person_id = picking_ids[0].confirm_person_id and picking_ids[
                        0].confirm_person_id.id or None
                    self.carrier_id = picking_ids[0].carrier_id and picking_ids[
                        0].carrier_id.id or None

    # @api.model
    # def create(self, vals):
    #     res = super(IssueLine, self).create(vals)
    #     print(res,'rescrete')
    #     resized = odoo.tools.image_get_resized_images(res.image_small, return_big=True, avoid_resize_medium=True)[
    #         'image_small']
    #     res.image_small = resized
    #     return res

    # @api.multi
    # def write(self, vals):
    #     res = super(IssueLine, self).write(vals)
    #     resized = odoo.tools.image_get_resized_images(self.image_small, return_big=True, avoid_resize_medium=True)[
    #         'image_small']
    #     rec.image_small = resized
    #     return res

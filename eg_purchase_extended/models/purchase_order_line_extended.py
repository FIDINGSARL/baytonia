from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.onchange("product_id")
    def eg_onchange_product_id(self):
        if self.product_id:
            if not self.product_id.sale_ok:
                raise ValidationError("Can be sold is not checked in {}".format(self.product_id.name))

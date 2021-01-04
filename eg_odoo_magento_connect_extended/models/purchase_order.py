from odoo import models, api
from odoo.exceptions import Warning


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.multi
    def update_quantity_magento(self):
        if self.state != "purchase":
            raise Warning("Purchase order is not confirmed")
        context = dict(self._context)
        context.update({"update": True})
        for order_line_id in self.order_line:
            order_line_id.product_id.with_context(context).update_product_quantity()

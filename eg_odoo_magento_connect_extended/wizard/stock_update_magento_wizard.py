from odoo import models, fields, api
from odoo.exceptions import ValidationError


class StockUpdateMagentoWizard(models.TransientModel):
    _name = "stock.update.magento.wizard"

    product_ids = fields.Many2many(comodel_name="magento.product", string="Products")
    all_product = fields.Boolean(string="All Product")
    product_limit = fields.Integer(string="Limit")
    is_success = fields.Boolean("Is success?")

    @api.multi
    def update_stock_in_magento(self):
        domain = [('pro_name.sale_ok', '=', True)]
        if self.product_ids:
            product_ids = self.product_ids.filtered(lambda l: l.pro_name.sale_ok)
        elif self.all_product:
            if self.product_limit:
                product_ids = self.env["magento.product"].search(domain, limit=self.product_limit)
            else:
                product_ids = self.env["magento.product"].search(domain)
        else:
            raise ValidationError("Either choose product or mark all product True")
        if product_ids:
            for product_id in product_ids:
                product_id.pro_name.update_product_quantity()
        self.is_success = True
        return {
            'view_mode': 'form',
            'res_id': self.id,
            'res_model': 'stock.update.magento.wizard',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'context': self.env.context,
            'target': 'new',
        }

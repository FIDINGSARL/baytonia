from odoo import models, fields, api
from odoo.exceptions import Warning


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.multi
    def set_barcode_product(self):
        if self.barcode:
            raise Warning("Please clear the old barcode!!! ")
        if self.default_code:
            if not self.default_code:
                raise Warning("Please set the SKU")
            self.barcode = self.default_code

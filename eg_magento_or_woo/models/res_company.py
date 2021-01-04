from odoo import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    connected_to = fields.Selection([('magento', 'Magento'),
                                     ('woo', 'WooCommerce'), ], string='Connected To')

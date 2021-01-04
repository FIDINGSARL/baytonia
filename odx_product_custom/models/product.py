from odoo import models,fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    reason_archive = fields.Char('Reason For Archive')
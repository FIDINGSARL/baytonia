from odoo import models, fields, api


class ResComapany(models.Model):
    _inherit = 'res.company'
    _description = 'Res Company'

    picking_policy = fields.Selection(
        [('direct', 'Deliver each product when available'), ('one', 'Deliver all products at once')],
        string='Shipping Policy')

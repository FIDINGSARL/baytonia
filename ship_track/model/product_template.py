from odoo import models, fields, api



class StockOrder(models.Model):
    _inherit = 'product.template'

    rack = fields.Char(string="Rack")
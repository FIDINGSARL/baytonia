from odoo import models,api,fields

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    source_doc = fields.Char('Purchase Source Doc', related='purchase_id.origin')
    comment = fields.Char('Comment')
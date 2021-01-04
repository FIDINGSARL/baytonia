from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    rfq_id = fields.Many2one('purchase.order', 'Request for Quotation', compute="_compute_rfq_id", )

    @api.depends('origin')
    def _compute_rfq_id(self):
        for do in self:
            rfq = self.env["purchase.order"].search([("origin", "ilike", do.origin)], limit=1)
            do.rfq_id = rfq.id

   

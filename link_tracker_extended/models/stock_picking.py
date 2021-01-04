from odoo import models, api


class StockPicking(models.Model):
    _inherit = "stock.picking"

    # @api.multi
    # def write(self, vals):
    #     res = super(StockPicking, self).write(vals)
    #     for rec in self.filtered(lambda p: p.sale_id and p.sale_id.carrier_details):
    #         link_tracker_id = self.env['link.tracker'].search([('sale_id', '=', rec.sale_id.id)])
    #         if link_tracker_id:
    #             link_tracker_id.write({
    #                 'title': rec.sale_id.name,
    #                 'url': rec.sale_id.carrier_details
    #             })
    #         elif vals.get('carrier_tracking_ref'):
    #             self.env['link.tracker'].create({
    #                 'title': rec.sale_id.name,
    #                 'sale_id': rec.sale_id.id,
    #                 'url': rec.sale_id.carrier_details
    #             })
    #     return res

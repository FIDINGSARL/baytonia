from odoo import models, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    _description = 'Eg Stock Picking'

    def action_done(self):
        res = super(StockPicking, self).action_done()
        if res:
            for rec in self:
                picking_barcode_ids = self.env['picking.barcode'].search([('picking_id', '=', rec.id)])
                picking_barcode_ids.write({'state': 'validate'})
        return res

    def action_cancel(self):
        res = super(StockPicking, self).action_cancel()
        if res:
            for rec in self:
                picking_barcode_ids = self.env['picking.barcode'].search([('picking_id', '=', rec.id)])
                picking_barcode_ids.write({'state': 'cancel'})
        return res

    @api.model
    def create(self, vals):
        res = super(StockPicking, self).create(vals)
        if res.picking_type_code == 'outgoing':
            picking_barcode_obj = self.env['picking.barcode']
            picking_barcode = picking_barcode_obj.create({
            })
            picking_barcode.picking_id = res.id
            picking_barcode.get_barcode_lines()
        return res

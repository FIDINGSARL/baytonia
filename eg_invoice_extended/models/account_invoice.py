from odoo import models, fields, api


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    picking_ids = fields.Many2many(comodel_name="stock.picking", string="Delivery Order",
                                   compute="_compute_picking_ids")
    picking_count = fields.Integer(string="Delivery Orders", compute="_compute_picking_count")

    @api.depends("invoice_line_ids")
    def _compute_picking_ids(self):
        for rec in self:
            if rec.invoice_line_ids:
                if rec.invoice_line_ids[0].sale_line_ids:
                    picking_ids = rec.invoice_line_ids[0].sale_line_ids[0].order_id.picking_ids
                    if picking_ids:
                        rec.picking_ids = picking_ids.ids
            else:
                rec.picking_ids = None

    @api.multi
    def view_action_delivery_order(self):
        action = self.env.ref('stock.action_picking_tree_all').read()[0]
        picking_ids = self.picking_ids
        if len(picking_ids) > 1:
            action['domain'] = [('id', 'in', picking_ids.ids)]
        elif picking_ids:
            action['views'] = [(self.env.ref('stock.view_picking_form').id, 'form')]
            action['res_id'] = picking_ids.id
        return action

    @api.depends("picking_ids")
    def _compute_picking_count(self):
        for rec in self:
            if rec.picking_ids:
                rec.picking_count = len(rec.picking_ids)
            else:
                rec.picking_count = 0

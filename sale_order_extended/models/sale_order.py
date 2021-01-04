from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    delivery_carrier_id_eg = fields.Many2one('delivery.carrier', string="Delivery Company",
                                             compute="_compute_delivery_carrier_id", store=True)
    # delivery_status_eg = fields.Char("Delivery States", compute="_compute_delivery_status_eg", store=True,
    #                                  readonly=True)
    # last_delivery_status_updated = fields.Datetime("Last Delivery Status Updated",
    #                                                compute="_compute_delivery_status_eg", store=True)
    repeat_count_eg = fields.Integer(related="partner_id.repeat_count_eg")
    issue_line_ids = fields.One2many(comodel_name="issue.line", inverse_name="order_id", string="Issue Lines")

    @api.depends('picking_ids', 'picking_ids.carrier_id', 'picking_ids.carrier_tracking_ref')
    @api.multi
    def _compute_delivery_carrier_id(self):
        for rec in self:
            picking_id = rec.picking_ids.filtered(lambda p: p.carrier_id and p.carrier_tracking_ref)
            if picking_id:
                rec.delivery_carrier_id_eg = picking_id[0].carrier_id.id


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def name_get(self):
        result = []
        issue_line = self._context.get("issue_line")
        if issue_line:
            for so_line in self:
                name = "{}".format(so_line.product_id.display_name)
                result.append((so_line.id, name))
            return result
        else:
            return super(SaleOrderLine, self).name_get()

    # @api.depends('smsa_delivery_status_eg')
    # @api.multi
    # def _compute_delivery_status_eg(self):
    #     for rec in self:
    #         # rec.delivery_status_eg = rec.smsa_delivery_status_eg or rec.vaal_delivery_status_eg or 'NO Update'
    #         rec.last_delivery_status_updated = fields.Datetime.now()

    # @api.depends('partner_id', 'partner_id.repeat_count_eg')
    # @api.multi
    # def _compute_repeat_count(self):
    #     for rec in self:
    #         rec.repeat_count_eg = rec.partner_id.repeat_count_eg

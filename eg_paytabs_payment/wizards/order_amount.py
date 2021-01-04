from odoo import models, fields, api


class OrderAmount(models.TransientModel):
    _name = "order.amount"

    @api.model
    def default_get(self, fields_list):
        res = super(OrderAmount, self).default_get(fields_list)
        sale_order_id = self.env["sale.order"].browse(self._context.get("active_id"))
        sms_instance_id = self.env["sms.instance"].search([("provider", "=", "unifonic_sms")])
        if sale_order_id and sms_instance_id:
            message = sms_instance_id.paytabs_message
            if message:
                message = message.replace("{{order_number}}", sale_order_id.name)
            if "total_amount" in fields_list:
                res["total_amount"] = sale_order_id.amount_total
                res["message"] = message
        return res

    total_amount = fields.Float(string="Total AMount", readonly=True)
    message = fields.Text(string="Message")
    discount = fields.Float(string="Discount")
    paytabs_configuration_id = fields.Many2one(comodel_name="paytabs.configuration", string="Instance", required=True)

    @api.multi
    def send_data_paytabs(self):
        order_id = self.env['sale.order'].browse(self._context.get("active_id"))
        if order_id:
            return order_id.post_data_paytabs(discount=self.discount, body=self.message, button=True,
                                       instance=self.paytabs_configuration_id)

    @api.onchange("discount")
    def onchange_discount(self):
        self.total_amount = self.total_amount - self.discount

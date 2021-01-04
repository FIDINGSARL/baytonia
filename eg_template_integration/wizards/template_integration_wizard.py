from odoo import models, fields, api


class TemplateIntegrationWizard(models.TransientModel):
    _name = "template.integration.wizard"

    template_id = fields.Many2one(comodel_name="sms.template", string="Template")
    body = fields.Text(string="Message")

    @api.onchange("template_id")
    def onchange_template_id(self):
        if self.template_id:
            active_model = self.env[self.template_id.model_id.model].browse(self._context.get("active_id"))
            partner_id = None
            if active_model.partner_id:
                partner_id = active_model.partner_id
            if active_model.sale_order_id and not partner_id:
                partner_id = active_model.sale_order_id.partner_id
                if not partner_id:
                    partner_id = active_model.sale_order_id.partner_shipping_id

            if active_model.stock_picking_id and not partner_id:
                partner_id = active_model.stock_picking_id.partner_id
            body = self.template_id.body
            body = body.replace("{{person_name}}", partner_id and partner_id.name or "")
            body = body.replace("{{ticket_number}}", active_model.ticket_number)
            self.body = body
        else:
            self.body = ""

    @api.multi
    def post_msg_by_template(self):
        active_model = self.env[self.template_id.model_id.model].browse(self._context.get("active_id"))
        if self.template_id.instance_id.provider == "unifonic_sms":
            if active_model:
                dst_number = None
                if active_model.partner_id:
                    dst_number = active_model.partner_id.phone or active_model.partner_id.mobile or None
                if active_model.sale_order_id and not dst_number:
                    dst_number = active_model.sale_order_id.partner_id.phone or active_model.sale_order_id.partner_id.mobile or None
                    if not dst_number:
                        dst_number = active_model.sale_order_id.partner_shipping_id.phone or active_model.sale_order_id.partner_shipping_id.mobile or None
                if active_model.stock_picking_id and not dst_number:
                    dst_number = active_model.stock_picking_id.partner_id.phone or active_model.stock_picking_id.partner_id.mobile or None
                if self.body and dst_number:
                    self.env["post.sms.wizard"].send_sms(body=self.body, dst_number=dst_number)

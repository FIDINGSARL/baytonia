from odoo import models, api, fields
from odoo.exceptions import Warning


class WizardSendToShipper(models.TransientModel):
    _name = 'wizard.send.to.shipper'

    @api.model
    def default_get(self, fields_list):
        res = super(WizardSendToShipper, self).default_get(fields_list)
        stock_picking_id = self.env["stock.picking"].browse(self._context.get("active_id"))
        amount = stock_picking_id.invoice_id.residual
        res['partner_id'] = stock_picking_id.partner_id.id
        res['picking_carrier_id'] = stock_picking_id.carrier_id.id
        if "cod_amount" in fields_list:
            res["cod_amount"] = amount
        if 'invisible_cod' in fields_list:
            group_id = self.env.ref("eg_send_to_shipper.send_to_shipper_manager")
            # if self.env.user.id in group_id.users.ids or (
            #         stock_picking_id.sale_id.payment_gateway_id and stock_picking_id.sale_id.payment_gateway_id.code in [
            #     "cod", "COD"]) or (
            #         stock_picking_id.sale_id.eg_magento_payment_method_id and stock_picking_id.sale_id.eg_magento_payment_method_id.code in [
            #     "cod", "COD"]):

            if self.env.user.id in group_id.users.ids or (
                    stock_picking_id.sale_id.eg_magento_payment_method_id and stock_picking_id.sale_id.eg_magento_payment_method_id.code in [
                "cod", "COD"]):

                res.update({"invisible_cod": True})
        return res

    carrier_id = fields.Many2one("delivery.carrier", string="Carrier", required=1)
    cod_amount = fields.Float(string="COD Amount")
    invisible_cod = fields.Boolean(string="Invisible")
    partner_id = fields.Many2one('res.partner', "Address")
    picking_carrier_id = fields.Many2one("delivery.carrier", string="Delivery Company")

    @api.multi
    def send_to_ship(self):
        stock_picking_id = self.env["stock.picking"].browse(self._context.get("active_id"))
        # if stock_picking_id.sale_id.payment_gateway_id and stock_picking_id.sale_id.payment_gateway_id.code in [
        #     "cod",
        #     "COD"] or stock_picking_id.sale_id.eg_magento_payment_method_id and stock_picking_id.sale_id.eg_magento_payment_method_id.code in [
        #     "cod", "COD"]:

        if stock_picking_id.sale_id.eg_magento_payment_method_id and stock_picking_id.sale_id.eg_magento_payment_method_id.code in [
            "cod", "COD"]:
            if self.cod_amount <= 50 and self.env.user.has_group('eg_send_to_shipper.send_to_shipper_restriction'):
                raise Warning(
                    "Are you sure this amount is correct? Please make sure so we don’t send a shipment with wrong amount")

        if self.invisible_cod:
            stock_picking_id.eg_cod_amount = self.cod_amount
        else:
            stock_picking_id.eg_cod_amount = 0
        context = self._context
        if context.get('active_ids', False):
            self.env.context = dict(self.env.context)
            self.env.context.update({'button': 'true'})
            shipping_active_id = self.env['stock.picking'].browse(context['active_id'])
            shipping_active_id.carrier_id = self.carrier_id
            shipping_active_id.send_to_shipper()
        return

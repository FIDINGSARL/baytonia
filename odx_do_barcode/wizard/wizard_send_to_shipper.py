from odoo import api, models, fields, _
from odoo.exceptions import UserError


class WizardSendToShipper(models.TransientModel):
    _inherit = 'wizard.send.to.shipper'

    not_ship = fields.Boolean("Shipment Warning Payment Method", default=False)
    not_ship_city = fields.Boolean("Shipment Warning City", default=False)


    @api.onchange('carrier_id')
    def on_change_carrier_id(self):
        if self.carrier_id:
            if self.carrier_id.eg_magento_payment_method_id:
                stock_picking_id = self.env["stock.picking"].browse(self._context.get("active_id"))
                if stock_picking_id.eg_magento_payment_method_id not in self.carrier_id.eg_magento_payment_method_id:
                    self.invisible_cod = False
                    self.not_ship = True
                else:
                    self.not_ship = False
            else:
                self.not_ship = False

            if self.carrier_id.state_ids:
                # if self.partner_id.state_id:
                if self.partner_id.state_id not in self.carrier_id.state_ids:
                    self.not_ship_city = True
                else:
                    self.not_ship_city = False
                # else:
                #     self.not_ship_city = False


    @api.multi
    def send_to_ship(self):
        if self.not_ship:
            raise UserError(_("Payment method is not valid for this delivery method"))
        if self.not_ship_city:
            raise UserError(_("This Company Doesn't Ship To This City"))
        return super(WizardSendToShipper, self).send_to_ship()

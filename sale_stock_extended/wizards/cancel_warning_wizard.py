from odoo import models, fields, api


class CancelWarningWizard(models.TransientModel):
    _name = "cancel.warning.wizard"

    @api.multi
    def cancel_order_warning(self):
        picking_id = self.env["stock.picking"].browse(self._context.get("active_id"))
        if picking_id:
            picking_id.action_cancel()

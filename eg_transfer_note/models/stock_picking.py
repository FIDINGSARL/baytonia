from odoo import models, fields


class StockPicking(models.Model):
    _inherit = "stock.picking"

    transfer_note = fields.Text("Transfer Note")

    def view_transfer_note(self):
        action = self.env.ref('eg_transfer_note.wizard_action_transfer_note_wizard').read()[0]
        return action

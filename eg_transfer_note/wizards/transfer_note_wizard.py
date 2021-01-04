from odoo import models, fields, api


class TransferNoteWizard(models.TransientModel):
    _name = "transfer.note.wizard"

    transfer_note = fields.Text("Transfer Note")

    @api.model
    def default_get(self, fields_list):
        res = super(TransferNoteWizard, self).default_get(fields_list)
        picking_id = self.env['stock.picking'].browse(self._context.get('picking_id'))
        if 'transfer_note' in fields_list:
            res.update({'transfer_note': picking_id.transfer_note})
        return res

    @api.multi
    def update_transfer_note(self):
        picking_id = self.env['stock.picking'].browse(self._context.get('picking_id'))
        picking_id.transfer_note = self.transfer_note

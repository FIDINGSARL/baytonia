from odoo import models, _
from odoo.exceptions import UserError


class OpenRecord(models.Model):
    _name = "open.record"
    _inherit = ['barcodes.barcode_events_mixin']

    def on_barcode_scanned(self, barcode):
        pickings = self.env['picking.barcode'].search([('picking_id.name', 'ilike', barcode)])
        if pickings:
            action = self.env.ref('eg_barcode.action_eg_barcode').read()[0]

            if len(pickings) > 1:
                action['domain'] = [('id', 'in', pickings.ids)]
            elif pickings:
                action['views'] = [(self.env.ref('eg_barcode.view_eg_picking_barcode_form').id, 'form')]
                action['res_id'] = pickings.id
            return action
        else:
            raise UserError(
                _('This barcode %s is not related to any record.') %
                barcode)

    def create(self, vals):
        print()
        return

    def write(self, vals):
        print()
        return

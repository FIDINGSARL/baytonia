from odoo import models, fields, api


class AddContactsToList(models.TransientModel):
    _name = "add.contacts.to.list"

    add_all_except_opt_out = fields.Boolean("Add all Except Opt-Out")
    recipient_ids = fields.Many2many('mail.mass_mailing.contact', string='Recipients')
    mailing_list_id = fields.Many2one('mail.mass_mailing.list', "Mailing List")

    @api.multi
    def add_to_mailing_list(self):
        recipient_ids = self.recipient_ids
        if self.add_all_except_opt_out:
            recipient_ids = self.env['mail.mass_mailing.contact'].search([('opt_out', '=', False)])
        for recipient_id in recipient_ids:
            recipient_id.list_ids = [(4, self.mailing_list_id.id)]

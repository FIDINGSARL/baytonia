import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class FavouriteCustomer(models.TransientModel):
    _name = "favourite.customer"

    name = fields.Char("Email list Name")
    order_count_gt = fields.Integer("Order Count >=")
    total_amount_gt = fields.Integer("Total Amount >=")

    @api.multi
    def action_create_email_list_eg(self):
        partner_ids = self.env['res.partner'].search(
            [('customer', '=', True), ('repeat_count_eg', '>=', self.order_count_gt), ('email', '!=', ''),
             ('total_ordered_amt_eg', '>=', self.total_amount_gt)])
        if partner_ids:
            mailing_list_id = self.env['mail.mass_mailing.list'].create({'name': self.name})
            for partner_id in partner_ids:
                exist = self.env['mail.mass_mailing.contact'].search([('email', '=', partner_id.email)], limit=1)
                if not exist:
                    exist = self.env['mail.mass_mailing.contact'].create(
                        {'name': partner_id.name,
                         'email': partner_id.email})
                exist.list_ids = [(4, mailing_list_id.id)]
                _logger.info(["=======", exist.email])
        return

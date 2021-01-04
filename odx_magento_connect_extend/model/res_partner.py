from odoo import models, api, _
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    _sql_constraints = [
        ('email_uniq', 'unique (email)', "Email should be Unique !")
    ]

    @api.model
    def create(self, vals):
        if vals.get("email"):
            existing_customer = self.search(
                [('email', '=', vals.get("email"))])
            if existing_customer:
                raise UserError(_("Email Already Exist"))
            else:
                return super(ResPartner, self).create(vals)
        else:
            return super(ResPartner, self).create(vals)

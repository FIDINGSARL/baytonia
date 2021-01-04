from odoo import models, api
from odoo.exceptions import AccessError


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        group_id = self.env.ref('eg_restrict_vendor_creation.group_vendor_create')
        if res.supplier and self.env.user.id not in group_id.users.ids and self.env.user.id != 1:
            raise AccessError("You do not have rights to create vendor!\nOnly {} Can create Vendors.".format(
                group_id.users.mapped("name")))
        return res

    @api.multi
    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        if 'active' in vals:
            group_id = self.env.ref('eg_restrict_vendor_creation.group_vendor_create')
            if self.supplier and self.env.user.id not in group_id.users.ids and self.env.user.id != 1:
                raise AccessError("You do not have rights to Active/Inactive vendor!\n"
                                  "Only {} Can Active/Inactive Vendors.".format(
                    group_id.users.mapped("name")))
        return res

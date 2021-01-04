from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ApproveStockPickingWizard(models.TransientModel):
    _name = 'approve.stock.picking.wizard'

    password = fields.Char("Password")
    approve_user_id = fields.Many2one("res.users", "User")

    @api.multi
    def approve_stock_picking(self):
        picking_id = self.env["stock.picking"].search([('id', '=', self._context.get('data_id'))])
        valid_pass = False
        self.env.cr.execute('SELECT password, password_crypt FROM res_users WHERE id=%s AND active',
                            (self.approve_user_id.id,))
        user = self.approve_user_id
        if self.env.cr.rowcount:
            stored, encrypted = self.env.cr.fetchone()
            if encrypted:
                valid_pass, replacement = user._crypt_context().verify_and_update(self.password, encrypted)
        if valid_pass:
            user_id = self.env["res.users"].sudo().search(
                [('id', '=', self.approve_user_id.id)], limit=1)
            group_id = self.env.ref('eg_inventory_user_validation.group_validate_picking')
            if user_id.id not in group_id.users.ids:
                raise ValidationError("User do Not have rights!!!")
        else:
            raise ValidationError("Invalid Password!!!")
        ctx = dict(self._context)
        ctx.update({"passed": True})
        res = picking_id.with_context(ctx).button_validate()
        return res

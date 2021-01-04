from odoo import fields, api, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    _description = 'Eg Picking Policy'

    picking_policy = fields.Selection(string='Shipping Policy', related="company_id.picking_policy")

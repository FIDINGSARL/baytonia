from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    lead_time = fields.Integer("Lead Time")
    supplier_type = fields.Selection([('local', 'Local'), ('global', 'Global'), ('expense', 'Expense')],
                                     string="Supplier Type")

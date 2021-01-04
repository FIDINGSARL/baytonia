from odoo import models, fields, api


class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    cause_of_damage = fields.Selection([('supplier_damage', 'Supplier Damage'), ('customer_damage', 'Customer Damage'),
                                        ('baytonia_damage', 'Baytonia Damage')], 'Cause Of Damage')
    cause_damage_id = fields.Many2one("couse.damage", string='Cause Of Damage')
    shipping_company_id = fields.Many2one('delivery.carrier', string='Shipping Company')
    attachment_ids = fields.One2many('ir.attachment', 'stock_scrap_id', 'Attachment', compute='compute_attachment_ids')

    def compute_attachment_ids(self):
        for rec in self:
            attachment_ids = self.env['ir.attachment'].search(
                [('res_model', '=', rec._name), ('res_id', '=', rec.id)])
            rec.attachment_ids = [(6, 0, attachment_ids.ids)]


class CouseDamage(models.Model):
    _name = 'couse.damage'

    name = fields.Char("Name", required=True)


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    stock_scrap_id = fields.Many2one('stock.scrap', 'Scrap Order')

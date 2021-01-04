from odoo import models, fields, api


class GroupMsg(models.Model):
    _name = "group.msg"

    name = fields.Char(string=" Group Name", required=True)
    total_numbers = fields.Integer(string="Total Members", compute="compute_on_total_numbers")
    number_list_ids = fields.One2many(comodel_name="number.list", inverse_name="group_msg_id", string="Number List")
    calling_code_id = fields.Many2one(comodel_name="calling.code", string="Country Group")

    @api.depends("number_list_ids")
    def compute_on_total_numbers(self):
        for rec in self:
            rec.total_numbers = len(rec.number_list_ids.mapped("number"))


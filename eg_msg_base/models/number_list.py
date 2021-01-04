from odoo import models, fields, api


class NumberList(models.Model):
    _name = "number.list"

    name = fields.Char(string="Name")
    number = fields.Char(string="Number", required=True)
    calling_code_id = fields.Many2one(comodel_name="calling.code", string="Calling Code")
    group_msg_id = fields.Many2one(comodel_name="group.msg", string="Msg Group")

    @api.model
    def default_get(self, fields_list):
        res = super(NumberList, self).default_get(fields_list)
        if 'calling_code_id' in fields_list:
            res['calling_code_id'] = self._context.get("calling_code_id")
        return res

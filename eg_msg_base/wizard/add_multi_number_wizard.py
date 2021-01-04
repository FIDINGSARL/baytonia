from odoo import models, fields, api


class AddMultiNumberWizard(models.TransientModel):
    _name = "add.multi.number.wizard"

    res_partner_ids = fields.Many2many(comodel_name="res.partner", string="Customers")

    @api.multi
    def add_multi_number(self):
        for res_partner_id in self.res_partner_ids:
            if res_partner_id.phone:
                number_fields = {"number": res_partner_id.phone,
                                 "name": res_partner_id.name,
                                 "group_msg_id": self._context.get("group_id")}

                if '+' in res_partner_id.phone:
                    calling_code_id = self.env["calling.code"].search([("name", "=", "Other")])
                    if not calling_code_id:
                        calling_code_id = self.env["calling.code"].create({"name": "Other"})
                    number_fields.update({"calling_code_id": calling_code_id.id})

                self.env["number.list"].create(number_fields)

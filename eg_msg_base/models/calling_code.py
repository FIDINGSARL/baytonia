from odoo import models, fields, api
import phonenumbers as pn
import pycountry


class CallingCode(models.Model):
    _name = "calling.code"

    name = fields.Char(string="Country")
    prefix_number = fields.Char(string="Prefix Number")

    @api.multi
    @api.depends('name', 'prefix_number')
    def name_get(self):
        result = []
        for country_code in self:
            name = ""
            if country_code.name:
                name += country_code.name
            if country_code.prefix_number:
                name += "({})".format(country_code.prefix_number)
            result.append((country_code.id, name))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=300):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('prefix_number', operator, name), ('name', operator, name)]

        calling_codes = self.search(domain + args, limit=limit)
        return calling_codes.name_get()

    @api.model
    def code_generate(self):
        country_code_list = {c.alpha_2: pn.country_code_for_region(c.alpha_2) for c in pycountry.countries}
        for country_name, value in country_code_list.items():
            prefix_number = "+" + str(value)
            if not self.search([("name", "=", country_name), ("prefix_number", "=", prefix_number)]):
                self.create({"name": country_name, "prefix_number": prefix_number})

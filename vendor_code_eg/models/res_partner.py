from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.osv.expression import get_unaccent_wrapper


class ResPartner(models.Model):
    _inherit = 'res.partner'

    vendor_code = fields.Char("Vendor Code")
    route_ids = fields.Many2many(comodel_name="stock.location.route", string="Routes",
                                 domain="[('product_selectable', '=', True)]")

    @api.constrains('vendor_code')
    def constraints_vendor_code(self):
        for rec in self:
            if rec.vendor_code:
                found = self.search([('id', '!=', rec.id), ('vendor_code', '=', rec.vendor_code)])
                if found:
                    raise ValidationError("Same Vendor code exist in :{}".format(found.mapped('name')))

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if args is None:
            args = []
        if name and operator in ('=', 'ilike', '=ilike', 'like', '=like'):
            self.check_access_rights('read')
            where_query = self._where_calc(args)
            self._apply_ir_rules(where_query, 'read')
            from_clause, where_clause, where_clause_params = where_query.get_sql()
            where_str = where_clause and (" WHERE %s AND " % where_clause) or ' WHERE '

            # search on the name of the contacts and of its company
            search_name = name
            if operator in ('ilike', 'like'):
                search_name = '%%%s%%' % name
            if operator in ('=ilike', '=like'):
                operator = operator[1:]

            unaccent = get_unaccent_wrapper(self.env.cr)

            query = """SELECT id
                             FROM res_partner
                          {where} ({email} {operator} {percent}
                               OR {display_name} {operator} {percent}
                               OR {reference} {operator} {percent}
                               OR {vat} {operator} {percent}
                               OR {vendor_code} {operator} {percent})
                               -- don't panic, trust postgres bitmap
                         ORDER BY {display_name} {operator} {percent} desc,
                                  {display_name}
                        """.format(where=where_str,
                                   operator=operator,
                                   email=unaccent('email'),
                                   display_name=unaccent('display_name'),
                                   reference=unaccent('ref'),
                                   percent=unaccent('%s'),
                                   vat=unaccent('vat'),
                                   vendor_code=unaccent('vendor_code'))

            where_clause_params += [search_name] * 6
            if limit:
                query += ' limit %s'
                where_clause_params.append(limit)
            self.env.cr.execute(query, where_clause_params)
            partner_ids = [row[0] for row in self.env.cr.fetchall()]

            if partner_ids:
                return self.browse(partner_ids).name_get()
            else:
                return []
        return super(ResPartner, self).name_search(name, args, operator=operator, limit=limit)

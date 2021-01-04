import binascii
import tempfile
import xlrd
from odoo import models,api, fields, _


class DeliveryCitiesImport(models.TransientModel):
    _name = 'delivery.cities.import'

    import_file = fields.Binary(string='Import File')

    @api.multi
    def update_cities(self, values,i):
        if values.get('english') and values.get('arabic'):
            state_id = self.find_state(values.get('english'),values.get('arabic'))
            if state_id:
                record = self.env['delivery.carrier'].search([('id', '=', self._context['active_id'])])
                if record:
                    record.update({'state_ids':[(4,state_id.id)]})
            else:
                return i

            # pricelist_id = self.find_currency(values.get('price_list'))

            # sale_id = sale_obj.create({
            #     'partner_id': partner_id.id,
            #     'pricelist_id': pricelist_id.id,
            # })
            # lines = self.make_order_line(values, sale_id)
        # else:
        #     sale_id = sale_obj.search([], limit=1).sorted(
        #     key=lambda r: r.id)
        #     lines = self.make_order_line(values, sale_id)

        # return lines
    # @api.multi
    # def make_order_line(self, values, sale_id):
    #     product_obj = self.env['product.product']
    #     order_line_obj = self.env['sale.order.line']
    #     product_search = product_obj.search([('default_code', '=', values.get('product'))], limit=1)
    #     product_uom = self.env['uom.uom'].search([('name', '=', values.get('uom'))], limit=1)
    #     if not product_uom:
    #         raise Warning(_('UOM is not defined'))
    #     tax_ids = []
    #     if values.get('tax'):
    #         if ';' in values.get('tax'):
    #             tax_names = values.get('tax').split(';')
    #             for name in tax_names:
    #                 tax = self.env['account.tax'].search([('name', '=', name), ('type_tax_use', '=', 'sale')])
    #                 if not tax:
    #                     raise Warning(_('"%s" Tax not in your system') % name)
    #                 tax_ids.append(tax.id)
    #
    #         elif ',' in values.get('tax'):
    #             tax_names = values.get('tax').split(',')
    #             for name in tax_names:
    #                 tax = self.env['account.tax'].search([('name', '=', name), ('type_tax_use', '=', 'sale')], limit=1)
    #                 if not tax:
    #                     raise Warning(_('"%s" Tax not in your system') % name)
    #                 tax_ids.append(tax.id)
    #         else:
    #             pass
    #     if product_search:
    #         product_id = product_search
    #     else:
    #         raise Warning(_('"%s" Product are not available') % values.get('product'))
    #     discount = 0
    #     if float(values.get('quantity')) > 0 and float(values.get('price')) > 0:
    #         if not ((float(values.get('quantity'))) * (float(values.get('price')))) == 0:
    #             discount = (float(values.get('discount')) / (
    #                     (float(values.get('quantity'))) * (float(values.get('price'))))) * 100
    #
    #     res = order_line_obj.create({
    #         'product_id': product_id.id,
    #         'product_uom_qty': values.get('quantity'),
    #         'name': product_id.name,
    #         'price_unit': values.get('price'),
    #         'product_uom': product_uom.id,
    #         'discount': discount,
    #         'order_id': sale_id.id,
    #     })
    #     if tax_ids:
    #         res.write({'tax_id': ([(6, 0, [tax_ids])])})
    #     return True
    # @api.multi
    # def find_currency(self, name):
    #     currency_obj = self.env['product.pricelist']
    #     currency_search = currency_obj.search([('name', '=', name)], limit=1)
    #     if currency_search:
    #         return currency_search
    #     else:
    #         raise Warning(_(' "%s" Pricelist are not available.') % name)
    @api.multi
    def find_state(self, english,arabic):
        state_obj = self.env['res.country.state']
        partner_search = state_obj.search(['|',('name', 'ilike', arabic),('name', 'ilike', english)], limit=1)
        if partner_search:
            return partner_search
        # else:
        #     raise Warning(_('"%s" Customer are not available') % name)
    @api.multi
    def import_cities(self):
        unicode = list
        fp = tempfile.NamedTemporaryFile(suffix=".xlsx")
        fp.write(binascii.a2b_base64(self.import_file))
        fp.seek(0)
        values = {}
        workbook = xlrd.open_workbook(fp.name)
        sheet = workbook.sheet_by_index(0)
        i = 0
        for row_no in range(sheet.nrows):
            i +=1
            val = {}
            rows = []
            if row_no <= 0:
                fields = map(lambda row: row.value.encode('utf-8'), sheet.row(row_no))
            else:
                line = list(
                    map(lambda row: isinstance(row.value, unicode) and row.value.encode('utf-8') or str(row.value),
                        sheet.row(row_no)))
                values.update({
                    'english': line[0],
                    'arabic': line[1],
                    # 'code': line[2],

                })
                # print(i)
                res = self.update_cities(values,i)
                # print(res)
        return res

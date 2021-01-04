import xlrd
from odoo import models, fields, api, _
import base64
import logging
from odoo.exceptions import Warning, ValidationError

_logger = logging.getLogger(__name__)


class Inventory(models.Model):
    _name = "stock.inventory"
    _inherit = ['stock.inventory', 'mail.thread', 'mail.activity.mixin']
    _description = "Inventory"
    _order = "date desc, id desc"

    attachment_data = fields.Binary(string="Import Inventory Attachment")
    file_name = fields.Char(string="File Name")

    @api.multi
    def download_template(self):
        attachment = self.env['ir.attachment'].search([('name', '=', 'import_template.xls')])
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % (attachment.id),
            'target': 'new',
            'nodestroy': False,
        }

    def import_attachment(self):
        if not self.attachment_data:
            raise Warning("File Not Found To Import")
        if self.file_name and self.file_name[-3:] != 'xls' and self.file_name[-4:] != 'xlsx':
            raise Warning("Please Provide Only .xls OR .xlsx File to Import Attachment!!!")

        worksheet = self.read_file(self.file_name, self.attachment_data)

        self.column_header = self.get_header(worksheet)

        if self.validate_column_header(self.column_header):
            consignment_order_data = self.get_data_from_file(worksheet, self.column_header)

            importable_data = self.validate_data(consignment_order_data)

            lines = self.env['stock.inventory.line']
            for line in importable_data:
                vals = {'product_qty': line.get('qty_available', 0),
                        'product_id': line.get('product_id'),
                        'inventory_id': self.id,
                        'location_id': self.location_id.id,
                        'prod_lot_id': line.get('prod_lot_id')
                        }
                lines.create(vals)
            return lines

    @api.multi
    def read_file(self, file_name, attachment_data):
        try:
            xl_workbook = xlrd.open_workbook(file_contents=base64.decodestring(attachment_data))
            worksheet = xl_workbook.sheet_by_index(0)
        except Exception as e:
            error_value = str(e)
            raise ValidationError(error_value)
        return worksheet

    @api.multi
    def get_header(self, worksheet):
        column_header = {}
        invalid_columns = []
        normal_columns = ['default_code', 'qty', 'prod_lot_id']
        for col_index in range(worksheet.ncols):
            value = worksheet.cell(0, col_index).value.lower()
            if value not in normal_columns:
                msg = "Invalid column found => " + str(value)
                invalid_columns.append(msg)
            else:
                column_header.update({col_index: value})

        if invalid_columns:
            raise ValidationError(str(invalid_columns))
        return column_header

    @api.multi
    def validate_column_header(self, column_header):
        require_fields = ['default_code', 'qty', 'prod_lot_id']
        missing = []
        for field in require_fields:
            if field not in column_header.values():
                missing.append(field)

        if len(missing) > 0:
            raise ValidationError("Please provide all the required fields in file, missing fields => %s." % (missing))
        return True

    @api.multi
    def get_data_from_file(self, worksheet, column_header):
        try:
            data = []
            for row_index in range(1, worksheet.nrows):
                sheet_data = {}
                for col_index in range(worksheet.ncols):
                    if bool(worksheet.cell(row_index, col_index).value):
                        sheet_data.update({column_header.get(col_index): worksheet.cell(row_index, col_index).value})
                if bool(sheet_data):
                    data.append(sheet_data)
        except Exception as e:
            error_value = str(e)
            raise ValidationError(error_value)
        return data

    @api.multi
    def validate_data(self, consignment_data=[]):
        product_obj = self.env['product.product']
        invalid_data = []
        importable_data = []

        for data in consignment_data:
            product_id = ''
            quantity = ''

            if type(data.get('default_code')) == float:
                default_code = str(int(data.get('default_code'))).strip()
            else:
                default_code = str((data.get('default_code'))).strip()

            if default_code:
                product_id = product_obj.search([('default_code', '=', default_code)])

                if not product_id:
                    msg = 'Product not found Of Related SKU !! " %s "' % (default_code)
                    invalid_data.append(msg)

                else:
                    if type(data.get('qty')) == type(0.0):
                        quantity = int(data.get('qty'))

                        prod_lot_id = self.env['stock.production.lot'].search(
                            [('name', '=', data.get('prod_lot_id'))])

                        vals = {
                            'product_id': product_id and product_id.id or '',
                            'product_name': product_id and product_id.display_name or '',
                            'qty_available': quantity,
                            'location_id': self.location_id.display_name,
                            'prod_lot_id': prod_lot_id.id,
                        }
                        importable_data.append(vals)

                    else:
                        msg = "Please give valid quantity"
                        invalid_data.append(msg)
            else:
                msg = "Please Given Product_SKU"
                invalid_data.append(msg)

        if len(invalid_data) > 0:
            print('invalid_data', invalid_data)
            self.message_post(invalid_data)
            # raise ValidationError("Please Correct Data First and then Import File.")
            return importable_data
            # return {}
        else:
            return importable_data

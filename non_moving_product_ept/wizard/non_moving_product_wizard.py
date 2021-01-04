import base64
import datetime
import logging
from datetime import datetime, date, timedelta
from io import BytesIO

from dateutil import parser

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)
try:
    import xlwt
    from xlwt import Borders
except ImportError:
    xlwt = None


class NonMovingProductWizard(models.TransientModel):
    _name = 'non.moving.product.wizard.ept'

    datas = fields.Binary('File')
    from_date = fields.Datetime(string="From Date", default=datetime.today() - timedelta(days=30), required=True)
    to_date = fields.Datetime(string="To Date", default=datetime.today(), required=True)
    warehouse_ids = fields.Many2many('stock.warehouse', string='Warehouses', required=True)

    # filter fields
    vendor_ids = fields.Many2many(comodel_name="res.partner", string="Vendors")
    category_ids = fields.Many2many(comodel_name="product.category", string="Categories")
    sale_price = fields.Float(string="Sale Price")
    cost_price = fields.Float(string="Cost Price")
    qty_available = fields.Float(string="Quantity On Hand")
    create_date_from = fields.Date(string="Create Date From")
    create_date_to = fields.Date(string="Create Date To")
    sku_condition = fields.Selection(
        [("ilike", "Contains"), ("not ilike", "Not Contain"), ("=", "is equal to"), ("!=", "is not equal to"),
         ("is_set", "is set"), ("not_set", "is not set")], string="SKU Condition")
    default_code = fields.Char(string="Internal Reference")
    name = fields.Char(string="Name")
    name_condition = fields.Selection(
        [("ilike", "Contains"), ("not ilike", "Not Contain"), ("=", "is equal to"), ("!=", "is not equal to"),
         ("is_set", "is set"), ("not_set", "is not set")], string="Name Condition")
    sale_price_condition = fields.Selection([("=", "="), ("<=", "<="), (">=", ">=")], string="Sale Condition")
    cost_price_condition = fields.Selection([("=", "="), ("<=", "<="), (">=", ">=")], string="Cost Condition")
    qty_available_condition = fields.Selection([("=", "="), ("<=", "<="), (">=", ">=")], string="QTY Condition")

    @api.constrains('from_date', 'to_date')
    def _check_value(self):
        if any(self.filtered(
                lambda value: value.from_date > str(datetime.today()) or value.to_date > str(datetime.today()))):
            raise ValidationError(_("Please select Dates which are not in Future"))
        if any(self.filtered(lambda value: value.from_date > value.to_date)):
            raise ValidationError(_("Enter the To Date Less than From Date"))

    @api.multi
    def send_non_moving_report_by_email(self):
        from_date = datetime.now() - timedelta(days=7)
        to_date = datetime.now()
        warehouse_ids = self.env["stock.warehouse"].search([("default_non_moving", "=", True)])
        if warehouse_ids:
            new_wizard = self.create({"from_date": from_date,
                                      "to_date": to_date,
                                      "warehouse_ids": [(6, 0, warehouse_ids.ids)]}).print_non_moving_product(
                from_cron="Weekly")

    @api.multi
    def print_non_moving_product(self, from_cron=None):
        active_id = self.ids[0]
        from_date = self.from_date
        to_date = self.to_date

        today = datetime.now().strftime("%Y-%m-%d")
        f_name = 'Non Moving Product' + ' ' + today

        warehouse_ids = self.warehouse_ids and self.warehouse_ids.ids or []

        self.get_non_moving_report(today, warehouse_ids, from_date, to_date)
        if self.datas:
            if from_cron == "Weekly":
                # email code starts
                cron_emails_id = self.env["cron.emails"].search([("report_type", "=", "non_moving_product")],
                                                                limit=1)
                if cron_emails_id:
                    duration = "{} to {}".format(from_date, to_date)
                    attachment_name = "Non Moving Product Report {}".format(
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))
                    attachment_id = self.env['ir.attachment'].create({
                        'name': attachment_name,
                        'type': 'binary',
                        'datas': self.datas,
                        'datas_fname': attachment_name + '.xls',
                        'store_fname': attachment_name,
                        'res_model': self._name,
                        'res_id': self.id,
                        'mimetype': 'application/x-xls'
                    })
                    # icpSudo = self.env['ir.config_parameter'].sudo()  # it is given all access
                    # email = icpSudo.get_param('eg_product_supplier_report.email_id', default="")

                    subject = "{} Non Moving Product Report".format(from_cron)

                    body_html = "<p>Hello</p></b> Please check {} Non Moving Product Report for duration {}.</b><p>Thanks</p>".format(
                        from_cron, duration)
                    values = {
                        'model': None,
                        'res_id': None,
                        'subject': subject,
                        'body': '',
                        'body_html': body_html,
                        'parent_id': None,
                        'attachment_ids': [(6, 0, [attachment_id.id])] or None,
                        'email_from': "karam@baytonia.com",
                        'email_to': cron_emails_id.emails,
                    }
                    mail_id = self.env['mail.mail']
                    mail_id.create(values).send()
            else:
                return {
                    'type': 'ir.actions.act_url',
                    'url': 'web/content/?model=non.moving.product.wizard.ept&download=true&field=datas&id=%s&filename=%s.xls' % (
                        active_id, f_name),
                    'target': 'self',
                }

    @api.multi
    def get_non_moving_report(self, today, warehouse_ids, from_date, to_date):
        warehouse_obj = self.env['stock.warehouse']
        warehouse_id_ls = warehouse_obj.search([('id', 'in', warehouse_ids)])
        workbook, header_bold, body_style, qty_cell_style, value_style, days_style = self.create_sheet()
        workbook, sheet_data, row_data = self.add_headings(warehouse_id_ls, workbook, header_bold, body_style,
                                                           qty_cell_style, value_style, days_style, from_date, to_date)
        data_dict = self.prepare_data(today, warehouse_ids, from_date, to_date)
        print_data = self.print_data(data_dict, workbook, sheet_data, row_data, header_bold, body_style, qty_cell_style,
                                     value_style,
                                     days_style)

        fp = BytesIO()
        workbook.save(fp)
        fp.seek(0)
        sale_file = base64.encodebytes(fp.read())
        fp.close()
        self.write({'datas': sale_file})

    @api.multi
    def non_moving_on_screen_report(self):
        active_id = self.ids[0]
        from_date = self.from_date
        to_date = self.to_date

        today = datetime.now().strftime("%Y-%m-%d")
        f_name = 'Non Moving Product' + ' ' + today
        warehouse_ids = self.warehouse_ids.ids
        if len(warehouse_ids) > 1:
            raise ValidationError(_("Please select only one Warehouse for On Screen Report."))

        non_moving_product_line = self.env['non.moving.product.line']
        non_moving_product_line.search([]).unlink()

        data_dict = self.prepare_data(today, warehouse_ids, from_date, to_date)
        for product_data in data_dict[self.warehouse_ids.id]:
            non_moving_product_line.create({
                'product_id': product_data.get('product_id'),
                'image_small': product_data.get('image_small'),
                'default_code': product_data.get('default_code'),
                'name': product_data.get('name'),
                'qty_available': product_data.get('qty_available'),
                'rack_location': product_data.get('rack_location') or '',
                # 'last_sale_date': product_data.get('last_sale_date') or "",
                'last_day_oldest': product_data.get('last_day_oldest') or "",
                'days_lpd': product_data.get('days_lpd') or "",
                # 'cost_of_product': product_data.get('cost_of_product'),       # TODO: New Change
                'total_cost': product_data.get('total_cost'),
                # 'last_purchase_date': product_data.get('last_purchase_date') or "",
                # 'sales_price': product_data.get('sales_price'),
                'total_sales_price': product_data.get('total_sales_price'),
                'sales_of_duration': product_data.get('sales_of_duration'),
                'total_sales': product_data.get('total_sales'),
                'warehouse_id': self.warehouse_ids.id,
                'start_date': from_date,
                'end_date': to_date,
            })

        action = self.env.ref('non_moving_product_ept.action_non_moving_product_line').read()[0]

        return action

    @api.multi
    def create_sheet(self):
        workbook = xlwt.Workbook()
        borders = Borders()
        header_border = Borders()
        header_border.left, header_border.right, header_border.top, header_border.bottom = Borders.THIN, Borders.THIN, Borders.THIN, Borders.THICK
        borders.left, borders.right, borders.top, borders.bottom = Borders.THIN, Borders.THIN, Borders.THIN, Borders.THIN
        header_bold = xlwt.easyxf(
            "font: bold on, height 200; pattern: pattern solid, fore_colour gray25;alignment: horizontal center ,vertical center")
        header_bold.borders = header_border
        body_style = xlwt.easyxf("font: height 200; alignment: horizontal left")
        body_style.borders = borders

        # # style for different colors in columns
        xlwt.add_palette_colour("light_blue_21", 0x21)
        workbook.set_colour_RGB(0x21, 176, 216, 230)
        qty_cell_style = xlwt.easyxf(
            "font: height 200,bold on, name Arial; align: horiz right, vert center;  pattern: pattern solid, fore_colour light_blue_21;  borders: top thin,right thin,bottom thin,left thin")

        xlwt.add_palette_colour("custom_orange", 0x22)
        workbook.set_colour_RGB(0x22, 255, 204, 153)
        value_style = xlwt.easyxf(
            "font: height 200,bold on, name Arial; align: horiz right, vert center;  pattern: pattern solid, fore_colour custom_orange;  borders: top thin,right thin,bottom thin,left thin")

        xlwt.add_palette_colour("custom_pink", 0x23)
        workbook.set_colour_RGB(0x23, 255, 204, 204)
        days_style = xlwt.easyxf(
            "font: height 200,bold on, name Arial; align: horiz right, vert center;  pattern: pattern solid, fore_colour custom_pink;  borders: top thin,right thin,bottom thin,left thin")

        return workbook, header_bold, body_style, qty_cell_style, value_style, days_style

    @api.multi
    def add_headings(self, warehouse_id_ls, workbook, header_bold, body_style, qty_cell_style, value_style, days_style,
                     from_date, to_date):
        sheet_data = {}
        row_data = {}
        for warehouse in warehouse_id_ls:
            warehouse.name_worksheet = workbook.add_sheet(warehouse.display_name, cell_overwrite_ok=True)
            warehouse.name_worksheet.row(7).height = 600
            warehouse.name_worksheet.col(0).width = 4000
            warehouse.name_worksheet.col(1).width = 5000
            warehouse.name_worksheet.col(2).width = 6000
            warehouse.name_worksheet.col(3).width = 4000
            warehouse.name_worksheet.col(4).width = 5000
            warehouse.name_worksheet.col(5).width = 6500

            warehouse.name_worksheet.write(7, 0, 'Product ID', header_bold)
            warehouse.name_worksheet.write(7, 1, 'Product Code', header_bold)
            warehouse.name_worksheet.write(7, 2, 'Product Name', header_bold)
            warehouse.name_worksheet.write(7, 3, 'Available Qty', header_bold)
            warehouse.name_worksheet.write(7, 4, 'Rack Location', header_bold)
            # warehouse.name_worksheet.write(7, 5, 'Last Sale Date', header_bold)  # TODO: New Change
            warehouse.name_worksheet.write(7, 5, 'Duration from Last sale\n(In days)', header_bold)
            warehouse.name_worksheet.write(7, 6, 'Days (Last Purchase Date)', header_bold)
            # warehouse.name_worksheet.write(7, 7, 'Last Purchase Date', header_bold)
            # warehouse.name_worksheet.write(7, 8, 'Unit Cost', header_bold)   # TODO: New Change
            warehouse.name_worksheet.write(7, 7, 'Total Cost', header_bold)
            # warehouse.name_worksheet.write(7, 10, 'Sales Price', header_bold)
            warehouse.name_worksheet.write(7, 8, 'Total Sales Price', header_bold)
            warehouse.name_worksheet.write(7, 9, 'Sales Of Duration', header_bold)
            warehouse.name_worksheet.write(7, 10, 'Total Sales', header_bold)

            # Title
            title = "Non Moving Products Report"
            warehouse.name_worksheet.write_merge(0, 0, 0, 10, title, header_bold)

            # Date
            string_datefrom = "Date From:"
            string_dateto = "Date To:"

            warehouse.name_worksheet.row(2).height = 300
            warehouse.name_worksheet.write(2, 0, string_datefrom, header_bold)
            warehouse.name_worksheet.write(2, 7, string_dateto, header_bold)
            warehouse.name_worksheet.write(2, 1, from_date)
            warehouse.name_worksheet.col(5).width = 6500
            warehouse.name_worksheet.write(2, 8, to_date)

            # # freezing columns
            warehouse.name_worksheet.set_panes_frozen(True)
            warehouse.name_worksheet.set_horz_split_pos(8)

            # #Get warehouse wise worksheet
            sheet_data.update({warehouse.id: warehouse.name_worksheet})

            # #initialize  worksheet wise row value
            row_data.update({warehouse.name_worksheet: 9})

        return workbook, sheet_data, row_data

    @api.multi
    def get_child_locations(self, location):

        child_list = []
        child_list.append(location.id)
        child_locations_obj = self.env['stock.location'].search(
            [('usage', '=', 'internal'), ('location_id', '=', location.id)])
        if child_locations_obj:
            for child_location in child_locations_obj:
                child_list.append(child_location.id)
                children_loc = self.get_child_locations(child_location)
                for child in children_loc:
                    child_list.append(child)
        return child_list

    @api.multi
    def prepare_data(self, today, warehouse_ids, from_date, to_date):
        data_dict = {}
        location_obj = self.env['stock.location']
        warehouse_obj = self.env['stock.warehouse']
        product_obj = self.env['product.product']
        stock_move_obj = self.env['stock.move']
        warehouse_ids = warehouse_obj.search([('id', 'in', warehouse_ids)])
        for warehouse in warehouse_ids:
            product_list = []
            child_locations = self.get_child_locations(warehouse.lot_stock_id)
            customer_location_ids = self.env['stock.location'].search([('usage', '=', 'customer')]).ids
            vendor_location_ids = self.env['stock.location'].search([('usage', '=', 'supplier')]).ids

            if len(child_locations) == 1:
                tuple_child_locations = tuple(child_locations)
                str_child_locations = str(tuple_child_locations).replace(',', '')

            else:
                str_child_locations = tuple(child_locations)
            if len(customer_location_ids) == 1:
                tuple_customer_location_ids = tuple(customer_location_ids)
                str_customer_location_ids = str(tuple_customer_location_ids).replace(',', '')
            else:
                str_customer_location_ids = tuple(customer_location_ids)
            if not child_locations or not customer_location_ids:
                return True
            product_list_qry = """select * from stock_move where (location_id in %s and location_dest_id in %s) and state='done' and date >= '%s' and date <='%s'""" % (
                str_child_locations, str_customer_location_ids, from_date, to_date)

            self._cr.execute(product_list_qry)
            move_ids = self._cr.dictfetchall()
            for move in move_ids:
                product = move.get('product_id')
                product_list.append(product)
            _logger.info(["======Products====", len(product_list)])
            domain = self.product_with_filter()
            all_internal_product_ids = product_obj.with_context(active_test=True).search(domain)  # TODO : New
            non_moving_product_ids = []

            for product in all_internal_product_ids:
                move_ids = stock_move_obj.search(
                    [('location_dest_id', 'in', child_locations), ('product_id', '=', product.id)])
                if move_ids:
                    oldest_date_str = min(move_ids.mapped('date'))
                    oldest_date = str(parser.parse(oldest_date_str).date())
                    if to_date < oldest_date:
                        continue
                if product.id not in product_list:
                    # _logger.info(["======Non-Moving Product====", product.id])
                    non_moving_product_ids.append(product.id)
                else:
                    _logger.info(["======Moving Product====", product.id])
            non_moving_product_ids = product_obj.search(
                [('id', 'in', non_moving_product_ids), ('type', '=', 'product')])
            output_location_ids = location_obj.search([('usage', '=', 'customer')])

            for product in non_moving_product_ids:
                total_sale = 0  # TODO: New Change
                days_lpd = 0
                sale_of_duration = 0
                if product.rack and product.rack == "BUN":  # TODO: New Change
                    continue
                new_sale_ids = self.env["sale.order"].search(
                    [("confirmation_date", ">=", product.create_date), ("confirmation_date", "<=", to_date),
                     ("state", "!=", "cancel")])
                if new_sale_ids:  # TODO: New Change
                    new_sale_line = self.env["sale.order.line"].search(
                        [("product_id", "=", product.with_context(
                            warehouse=warehouse.id).id), ("order_id", "in", new_sale_ids.ids)])
                    total_sale = sum(new_sale_line.mapped("product_uom_qty"))
                sale_ids = self.env["sale.order"].search(
                    [("confirmation_date", ">=", from_date), ("confirmation_date", "<=", to_date),
                     ("state", "!=", "cancel")])
                if sale_ids:  # TODO: New Change
                    sale_line = self.env["sale.order.line"].search(
                        [("product_id", "=", product.id), ("order_id", "in", sale_ids.ids)])
                    sale_of_duration = sum(sale_line.mapped("product_uom_qty"))
                last_sale_date = stock_move_obj.search(
                    [('location_id', 'in', child_locations), ('location_dest_id', 'in', output_location_ids.ids),
                     ('product_id', '=', product.id)], limit=1, order="date desc")
                last_purchase_date = stock_move_obj.search(
                    [('location_id', 'in', vendor_location_ids), ('location_dest_id', 'in', child_locations),
                     ('product_id', '=', product.id)], limit=1, order="date desc")
                if last_purchase_date:
                    last_purchase_date = datetime.strptime(last_purchase_date.date,
                                                           "%Y-%m-%d %H:%M:%S")  # TODO: New Change
                    new_to_date = datetime.strptime(to_date, "%Y-%m-%d %H:%M:%S")
                    days_lpd = (new_to_date - last_purchase_date).days
                qty = product.with_context(warehouse=warehouse.id).qty_available
                quantity = False
                if self.qty_available_condition:
                    if self.qty_available_condition == "=":
                        if qty == self.qty_available:
                            quantity = True
                    elif self.qty_available_condition == "<=":
                        if qty <= self.qty_available:
                            quantity = True
                    elif self.qty_available_condition == ">=":
                        if qty >= self.qty_available:
                            quantity = True
                else:
                    quantity = True
                if quantity:
                    last_day_oldest = self.days_oldest(last_sale_date.date)
                    if data_dict.get(warehouse.id):
                        data_dict.get(warehouse.id).append(
                            {'product_id': product.id,
                             'default_code': product.default_code,
                             'name': product.name,
                             'qty_available': product.with_context(
                                 warehouse=warehouse.id).qty_available,
                             'rack_location': product.rack or '',
                             # 'last_sale_date': last_sale_date.date or "",
                             'last_day_oldest': last_day_oldest or "",
                             'days_lpd': days_lpd,
                             # 'cost_of_product': product.standard_price,
                             'total_cost': product.with_context(
                                 warehouse=warehouse.id).qty_available * product.standard_price,
                             # 'last_purchase_date': last_purchase_date.date or "",
                             # 'sales_price': product.list_price,
                             'total_sales_price': product.with_context(
                                 warehouse=warehouse.id).qty_available * product.list_price,
                             'total_sales': total_sale,
                             'sales_of_duration': sale_of_duration,
                             'image_small': product.image_small,
                             })
                    else:
                        data_dict.update({
                            warehouse.id: [{'product_id': product.id,
                                            'default_code': product.default_code,
                                            'name': product.name,
                                            'qty_available': product.with_context(
                                                warehouse=warehouse.id).qty_available,
                                            'rack_location': product.rack or '',
                                            # 'last_sale_date': last_sale_date.date or "",
                                            'last_day_oldest': last_day_oldest or "",
                                            'days_lpd': days_lpd,
                                            # 'cost_of_product': product.standard_price,
                                            'total_cost': product.with_context(
                                                warehouse=warehouse.id).qty_available * product.standard_price,
                                            # 'last_purchase_date': last_purchase_date.date or "",
                                            # 'sales_price': product.list_price,
                                            'total_sales_price': product.with_context(
                                                warehouse=warehouse.id).qty_available * product.list_price,
                                            'total_sales': total_sale,
                                            'sales_of_duration': sale_of_duration,
                                            'image_small': product.image_small,
                                            }]})

        return data_dict

    @api.multi
    def days_oldest(self, last_sale_date):
        if not last_sale_date:
            return 0
        today = datetime.strptime(str(datetime.now().date()), '%Y-%m-%d').strftime('%m-%d-%Y')
        current_date = datetime.strptime(str(today), '%m-%d-%Y').date()
        someday = last_sale_date
        time = someday[:4] + '-' + someday[5:7] + '-' + someday[8:10]
        time_validation = datetime.strptime(str(time), '%Y-%m-%d').strftime('%m-%d-%Y')
        final_date = datetime.strptime(str(time_validation), '%m-%d-%Y').date()
        diff = current_date - final_date
        return diff.days

    @api.multi
    def print_data(self, data_dict, workbook, sheet_data, row_data, header_bold, body_style, qty_cell_style,
                   value_style, days_style):
        column = 0
        if data_dict:
            for warehouse_id, data_details in data_dict.items():
                for product_data in data_details:
                    row = row_data[sheet_data[warehouse_id]]
                    sheet_data[warehouse_id].row(row).height = 350
                    sheet_data[warehouse_id].write(row, column, product_data.get('product_id'), body_style)
                    sheet_data[warehouse_id].write(row, column + 1, product_data.get('default_code') or '-', body_style)
                    sheet_data[warehouse_id].write(row, column + 2, product_data.get('name'), body_style)
                    sheet_data[warehouse_id].write(row, column + 3, product_data.get('qty_available'), qty_cell_style)
                    sheet_data[warehouse_id].write(row, column + 4, product_data.get('rack_location'), qty_cell_style)
                    # sheet_data[warehouse_id].write(row, column + 5, product_data.get('last_sale_date'), value_style)
                    sheet_data[warehouse_id].write(row, column + 5, product_data.get('last_day_oldest'), days_style)
                    sheet_data[warehouse_id].write(row, column + 6, product_data.get('days_lpd'), days_style)
                    # sheet_data[warehouse_id].write(row, column + 7, product_data.get('last_purchase_date'),
                    #                                qty_cell_style)
                    # sheet_data[warehouse_id].write(row, column + 8, product_data.get('cost_of_product'), qty_cell_style)
                    sheet_data[warehouse_id].write(row, column + 7, product_data.get('total_cost'), qty_cell_style)
                    # sheet_data[warehouse_id].write(row, column + 10, product_data.get('sales_price'), qty_cell_style)
                    sheet_data[warehouse_id].write(row, column + 8, product_data.get('total_sales_price'),
                                                   qty_cell_style)
                    sheet_data[warehouse_id].write(row, column + 9, product_data.get('sales_of_duration'), days_style)
                    sheet_data[warehouse_id].write(row, column + 10, product_data.get('total_sales'), days_style)
                    row += 1
                    # Increse row
                    row_data.update({sheet_data[warehouse_id]: row})

        else:
            return False

    @api.multi
    def product_with_filter(self):
        domain = []
        if self.category_ids:
            domain.append(('categ_ids', 'in', self.category_ids.ids))
        if self.vendor_ids:
            supplier_info_ids = self.env['product.supplierinfo'].search([('name', 'in', self.vendor_ids.ids)])
            domain.append(('seller_ids', 'in', supplier_info_ids.ids))
        if self.cost_price_condition:
            domain.append(('standard_price', self.cost_price_condition, self.cost_price))
        if self.sale_price_condition:
            domain.append(('lst_price', self.sale_price_condition, self.sale_price))
        if self.create_date_from:
            domain.append(('create_date', '>=', self.create_date_from))
        if self.create_date_to:
            domain.append(('create_date', '<=', self.create_date_to))
        if self.sku_condition and self.default_code:
            if self.sku_condition in ["is_set", "not_set"]:
                if self.sku_condition == "is_set":
                    domain.append(('default_code', 'not in', [None, False, ""]))
                else:
                    domain.append(('default_code', 'in', [None, False, ""]))
            else:
                domain.append(('default_code', self.sku_condition, self.default_code))
        if self.name_condition and self.name:
            if self.name_condition in ["is_set", "not_set"]:
                if self.name_condition == "is_set":
                    domain.append(('name', 'not in', [None, False, ""]))
                else:
                    domain.append(('name', 'in', [None, False, ""]))
            else:
                domain.append(('name', self.name_condition, self.name))
        return domain

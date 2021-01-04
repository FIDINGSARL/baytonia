import base64
from datetime import datetime, date, timedelta
from io import BytesIO
from dateutil.relativedelta import relativedelta
from dateutil import parser
from odoo import models, fields, api
import xlwt
import logging

_logger = logging.getLogger(__name__)


class HpStockReport(models.TransientModel):
    _name = "hp.stock.report"

    @api.model
    def _default_from_date(self):
        return date.today() - timedelta(days=7)

    file_name = fields.Char(string="File Name")
    data = fields.Binary(string="Data")
    to_date = fields.Date(string="To Date", default=date.today(), required=True)
    from_date = fields.Date(string="From Date", default=_default_from_date, required=True)

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
    average_sale_price = fields.Boolean(string="Average Sale Price")
    sale_extra_data = fields.Boolean(string="Sale Extra Data")
    add_custom_filter = fields.Boolean('Add Custom Filter')
    filter_option = fields.Selection(
        [("qoh", "QTY On Hand"), ("sale_qty", "QTY Sold"), ('revenue', "Revenue"), ("profit", "Profit"),
         ("total_out", "Total Out (%)"), ("total_out_create_date", "Total Out (Since Create Date)"),
         ('total_cost', "Total Cost"), ('total_in_create_date', "Total IN (Since Create Date)")], default='qoh',
        string="Filter")
    filter_range = fields.Selection(
        [("greater", "greater than"), ("less", "less than")], default='greater', string="Filter Value")
    filter_value = fields.Float('Value')

    @api.multi
    def generate_stock_product_on_screen_report(self):
        self.env['hp.stock.line'].search([]).unlink()
        current_date = date.today()
        serial_no = 1
        supplier_info_ids = self.env['product.supplierinfo'].search([('name', 'in', self.vendor_ids.ids)])
        if supplier_info_ids:
            product_tmpl_ids = supplier_info_ids.mapped('product_tmpl_id')
            product_ids = product_tmpl_ids.mapped('product_variant_ids')

        else:
            product_ids = self.env["product.product"].search([])
        domain = []
        if self.category_ids:
            domain.append(('categ_ids', 'in', self.category_ids.ids))
        if self.qty_available_condition:
            domain.append(('qty_available', self.qty_available_condition, self.qty_available))
        if self.cost_price_condition:
            domain.append(('standard_price', self.cost_price_condition, self.cost_price))
        if self.sale_price_condition:
            domain.append(('product_tmpl_id.lst_price', self.sale_price_condition, self.sale_price))
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
        product_ids = product_ids.search(domain + [('id', 'in', product_ids.ids)])

        mto_id = self.env.ref('stock.route_warehouse0_mto').id
        mto_mts_id = self.env.ref("stock_mts_mto_rule.route_mto_mts").id

        sale_order_ids = self.env["sale.order"].search(
            [("confirmation_date", ">=", self.from_date), ("confirmation_date", "<=", self.to_date),
             ("state", "!=", "cancel")])
        purchase_order_ids = self.env["purchase.order"].search(
            [("date_order", ">=", self.from_date), ("date_order", "<=", self.to_date),
             ("state", "!=", "cancel")])
        to_date = datetime.strptime(self.to_date, "%Y-%m-%d")
        from_date = datetime.strptime(self.from_date, "%Y-%m-%d")

        if sale_order_ids:
            total_qty_sold = 0
            for product_id in product_ids:
                total_in = 0
                average_sale_price = 0
                data_dict = {}
                sale_per_day = []
                # new_total_out = 0
                # new_total_in = 0
                new_out_in = 0
                total_in_percentage = 0.0
                total_out_percentage = 0.0
                avg_sale_day = 0
                avg_revenue_day = 0
                # total_out = 0
                # sale_qty = 0
                total_avg_sale_price = 0
                sale_line_ids = self.env["sale.order.line"].search(
                    [("product_id", "=", product_id.id), ("order_id", "in", sale_order_ids.ids)])
                sale_qty = sum(sale_line_ids.mapped("product_uom_qty"))
                d1 = parser.parse(self.from_date).date()
                d2 = parser.parse(self.to_date).date()
                dates_btwn = d1
                date_list = []
                while dates_btwn <= d2:
                    dates_btwn = dates_btwn + relativedelta(days=1)
                    date_to_d = str(dates_btwn) + ' ' + '23:59:59'
                    date_from_d = str(dates_btwn) + ' ' + '00:00:00'
                    sale_order_ids_date = self.env["sale.order"].search(
                        [("confirmation_date", ">=", date_from_d), ("confirmation_date", "<=", date_to_d),
                         ("state", "!=", "cancel")])
                    sale_line_ids_date = self.env["sale.order.line"].search(
                        [("product_id", "=", product_id.id), ("order_id", "in", sale_order_ids_date.ids)])
                    if sale_line_ids_date:
                        sale_qty_date = sum(sale_line_ids_date.mapped("product_uom_qty"))
                        if sale_qty_date:
                            date_list.append(date_from_d)
                        sale_per_day.append(sale_qty_date)

                if not sale_qty:
                    continue
                if self.average_sale_price:
                    total_sale_price = 0
                    for sale_line_id in sale_line_ids:
                        total_sale_price += sale_line_id.product_uom_qty * sale_line_id.price_unit
                    average_sale_price = round(total_sale_price / sale_qty, 2)
                    total_avg_sale_price = average_sale_price * sale_qty
                total_qty_sold += sale_qty
                revenue = sale_qty * product_id.lst_price
                count_sale_order = len(list(dict.fromkeys(sale_line_ids.mapped("order_id"))))
                total_out = sum(sale_line_ids.mapped("qty_delivered"))
                create_date = datetime.strptime(product_id.create_date, "%Y-%m-%d %H:%M:%S")
                total_days = (to_date - create_date).days
                from_date = datetime.strptime(self.from_date, "%Y-%m-%d")
                duration_days = (to_date - from_date).days

                if purchase_order_ids:
                    total_in = sum(self.env["purchase.order.line"].search(
                        [("product_id", "=", product_id.id), ("order_id", "in", purchase_order_ids.ids)]).mapped(
                        "qty_received"))
                # new_sale_ids = self.env["sale.order"].search([("state", "!=", "cancel")])
                new_total_out = sum(self.env["sale.order.line"].search(
                    [("product_id", "=", product_id.id), ("order_id.state", "!=", "cancel")]).mapped(
                    "qty_delivered"))
                # new_purchase_ids = self.env["purchase.order"].search([("state", "!=", "cancel")])
                new_total_in = sum(self.env["purchase.order.line"].search(
                    [("product_id", "=", product_id.id), ("order_id.state", "!=", "cancel")]).mapped(
                    "qty_received"))

                qoh = product_id.qty_available
                avg_revenue_day = revenue / duration_days
                avg_sale_day = sale_qty / duration_days
                if qoh < 1 and self.sale_extra_data:
                    if date_list:
                        end_date = datetime.strptime(date_list[-1], "%Y-%m-%d %H:%M:%S")
                    day_range = (end_date - from_date).days if date_list else 0
                    avg_revenue_day = revenue / day_range if day_range != 0 else 0
                    avg_sale_day = sale_qty / day_range if day_range != 0 else 0
                profit = product_id.lst_price - product_id.standard_price
                if new_total_in:
                    total_in_percentage = round((total_in * 100) / new_total_in, 2)
                if new_total_out:
                    total_out_percentage = round((total_out * 100) / new_total_out, 2)
                if new_total_in:
                    new_out_in = round(new_total_out / new_total_in, 2)
                # total_in_percentage = "{} %".format(total_in_percentage)
                # total_out_percentage = "{} %".format(total_out_percentage)
                # forcasted_profit = qoh * profit
                if mto_id in product_id.route_ids.ids or mto_mts_id in product_id.route_ids.ids:
                    make_to_order = "YES"
                else:
                    make_to_order = "NO"
                if product_id.categ_ids:
                    category_list = [category_id.display_name for category_id in product_id.categ_ids]
                else:
                    category_list = [""]
                vendor = product_id.seller_ids and product_id.seller_ids[0].name or ""
                data_dict.update({
                    'serial_no': serial_no,
                    'product_id': product_id.id,
                    'image_small': product_id.image_small,
                    'days_since_creation': total_days,
                    'qty_available': qoh,
                    'qty_sold': sale_qty,
                    'frequency_of_sale': count_sale_order,
                    'total_out': total_out_percentage,
                    'total_in': total_in_percentage,
                    'total_out_scd': new_total_out,
                    'total_in_scd': new_total_in,
                    'total_out_in': new_out_in,
                    'lst_price': product_id.lst_price,
                    'standard_price': product_id.standard_price,
                    'total_cost': product_id.standard_price * qoh,
                    'profit': profit,
                    'revenue': revenue,
                    'make_to_order': make_to_order,
                    'category': " || ".join(category_list),
                    'from_date': self.from_date,
                    'to_date': self.to_date,
                    'avg_revenue_day': avg_revenue_day,
                    'vendor': vendor and vendor.id or "",
                    'average_sale_price': self.average_sale_price and average_sale_price or "",
                    'avg_sale_day': avg_sale_day,
                    'max_sale_day': max(sale_per_day) if sale_per_day else 0,
                    'min_sale_day': min(sale_per_day) if sale_per_day else 0,
                    'total_avg_sale_price': total_avg_sale_price
                })
                serial_no += 1

                self.env['hp.stock.line'].create(data_dict)

        action = self.env.ref('eg_hero_product_report.action_hero_product_stock_line').read()[0]
        return action

    @api.multi
    def generate_stock_product_report(self, from_cron=None):
        # current_date = date.today()
        duration = "{} to {}".format(self.from_date, self.to_date)
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet("My Worksheet")
        header2 = xlwt.easyxf(
            "font:height 200;border:top thin,right thin,bottom thin,left thin; pattern:fore_colour gray25; alignment: horiz center ,vert center ")
        header4 = xlwt.easyxf(
            "font:bold on, height 220;border:top thin,right thin,bottom thin,left thin; pattern:fore_colour gray25; alignment: horiz center ,vert center ")
        header1 = xlwt.easyxf(
            "font: bold on, height 300;border:top thin,right thin,bottom thin,left thin; pattern:pattern solid, fore_colour gray25; alignment: horiz center ,vert center ")
        header3 = xlwt.easyxf(
            "font: bold on, height 260;border:top thin,right thin,bottom thin,left thin; pattern:pattern solid, fore_colour gray25; alignment: horiz center ,vert center ")
        serial_no = 1
        row = 0
        column = 0

        fnames = ["Serial No", "Name", "Days Since Creation", "QTY On Hand", "Vendor", "QTY Sold",
                  "Frequency", "Total Out (%)", "Total Out (Since Create Date)",
                  "Total IN (Since Create Date)", "Total Out/In", "Sale Price", "Cost Price", "Revenue", "Total Cost",
                  "Profit", "Make to Order", "Category", "Supplier Type"]
        if self.average_sale_price:
            fnames.append("Average Sale Price")
            fnames.append("Avg Sale Price * QTY Sold")
        if self.sale_extra_data:
            fnames.append("Last Cycle Sales / Day")
            fnames.append("Avg Revenue/Day")
            fnames.append("Max Sales /Day")
            fnames.append("Min Sales /Day")

        worksheet.write_merge(row, row, column, len(fnames) - 1, "List Of Stock Product", header1)
        row += 2
        worksheet.write_merge(row, row, column, len(fnames) - 1, duration, header1)
        row += 2
        for header_name in fnames:
            worksheet.write(row, column, header_name, header3)
            column += 1
        row += 1

        supplier_info_ids = self.env['product.supplierinfo'].search([('name', 'in', self.vendor_ids.ids)])
        if supplier_info_ids:
            product_tmpl_ids = supplier_info_ids.mapped('product_tmpl_id')
            product_ids = product_tmpl_ids.mapped('product_variant_ids')

        else:
            product_ids = self.env["product.product"].search([])
        domain = []
        if self.category_ids:
            domain.append(('categ_ids', 'in', self.category_ids.ids))
        if self.qty_available_condition:
            domain.append(('qty_available', self.qty_available_condition, self.qty_available))
        if self.cost_price_condition:
            domain.append(('standard_price', self.cost_price_condition, self.cost_price))
        if self.sale_price_condition:
            domain.append(('product_tmpl_id.lst_price', self.sale_price_condition, self.sale_price))
        if self.create_date_from:
            domain.append(('create_date', '>=', self.create_date_from))
        if self.create_date_to:
            domain.append(('create_date', '<=', self.create_date_to))
        if self.sku_condition and self.default_code or self.sku_condition in ["is_set", "not_set"]:
            if self.sku_condition in ["is_set", "not_set"]:
                if self.sku_condition == "is_set":
                    domain.append(('default_code', 'not in', [None, False, ""]))
                else:
                    domain.append(('default_code', 'in', [None, False, ""]))
            else:
                domain.append(('default_code', self.sku_condition, self.default_code))
        if self.name_condition and self.name or self.name_condition in ["is_set", "not_set"]:
            if self.name_condition in ["is_set", "not_set"]:
                if self.name_condition == "is_set":
                    domain.append(('name', 'not in', [None, False, ""]))
                else:
                    domain.append(('name', 'in', [None, False, ""]))
            else:
                domain.append(('name', self.name_condition, self.name))
        product_ids = product_ids.search(domain + [('id', 'in', product_ids.ids)])

        mto_id = self.env.ref('stock.route_warehouse0_mto').id
        mto_mts_id = self.env.ref("stock_mts_mto_rule.route_mto_mts").id
        sale_order_ids = self.env["sale.order"].search(
            [("confirmation_date", ">=", self.from_date), ("confirmation_date", "<=", self.to_date),
             ("state", "!=", "cancel")])
        # purchase_order_ids = self.env["purchase.order"].search(
        #     [("date_order", ">=", self.from_date), ("date_order", "<=", self.to_date)])
        to_date = datetime.strptime(self.to_date, "%Y-%m-%d")
        from_date = datetime.strptime(self.from_date, "%Y-%m-%d")
        supplier_type = {
            'local': 'Local',
            'global': 'Global',
        }
        if sale_order_ids:
            total_qty_sold = 0
            for product_id in product_ids:
                supplier_type_value = ''
                if product_id.seller_ids:
                    if product_id.seller_ids[0].supplier_type:
                        supplier_type_value = supplier_type[product_id.seller_ids[0].supplier_type]
                total_out_percentage = 0.0
                new_out_in = 0
                average_sale_price = 0
                sale_line_ids = self.env["sale.order.line"].search(
                    [("product_id", "=", product_id.id), ("order_id", "in", sale_order_ids.ids)])
                sale_qty = sum(sale_line_ids.mapped("product_uom_qty"))
                if not sale_qty:
                    continue
                if self.average_sale_price:
                    total_sale_price = 0
                    for sale_line_id in sale_line_ids:
                        total_sale_price += sale_line_id.product_uom_qty * sale_line_id.price_unit
                    average_sale_price = round(total_sale_price / sale_qty, 2)
                    total_avg_sale_price = average_sale_price * sale_qty

                if self.sale_extra_data:
                    d1 = parser.parse(self.from_date).date()
                    d2 = parser.parse(self.to_date).date()
                    dates_btwn = d1
                    date_list = []
                    sale_per_day = []
                    while dates_btwn <= d2:
                        dates_btwn = dates_btwn + relativedelta(days=1)
                        date_to_d = str(dates_btwn) + ' ' + '23:59:59'
                        date_from_d = str(dates_btwn) + ' ' + '00:00:00'
                        sale_order_ids_date = self.env["sale.order"].search(
                            [("confirmation_date", ">=", date_from_d), ("confirmation_date", "<=", date_to_d),
                             ("state", "!=", "cancel")])
                        sale_line_ids_date = self.env["sale.order.line"].search(
                            [("product_id", "=", product_id.id), ("order_id", "in", sale_order_ids_date.ids)])
                        if sale_line_ids_date:
                            sale_qty_date = sum(sale_line_ids_date.mapped("product_uom_qty"))
                            if sale_qty_date:
                                date_list.append(dates_btwn)
                            sale_per_day.append(sale_qty_date)

                # total_qty_sold += sale_qty
                count_sale_order = len(list(dict.fromkeys(sale_line_ids.mapped("order_id"))))
                # above use for remove sem item
                total_out = sum(sale_line_ids.mapped("qty_delivered"))
                revenue = sale_qty * product_id.lst_price
                create_date = datetime.strptime(product_id.create_date, "%Y-%m-%d %H:%M:%S")
                total_days = (to_date - create_date).days
                duration_days = (to_date - from_date).days
                avg_revenue_day = revenue / duration_days
                avg_sale_day = sale_qty / duration_days
                # if purchase_order_ids:
                #     total_in = sum(self.env["purchase.order.line"].search(
                #         [("product_id", "=", product_id.id), ("order_id", "in", purchase_order_ids.ids)]).mapped(
                #         "qty_received"))
                # new_sale_ids = self.env["sale.order"].search([("state", "!=", "cancel")])
                new_total_out = sum(self.env["sale.order.line"].search(
                    [("product_id", "=", product_id.id), ("order_id.state", "!=", "cancel")]).mapped(
                    "qty_delivered"))
                # new_purchase_ids = self.env["purchase.order"].search([("state", "!=", "cancel")])
                new_total_in = sum(self.env["purchase.order.line"].search(
                    [("product_id", "=", product_id.id), ("order_id.state", "!=", "cancel")]).mapped(
                    "qty_received"))

                qoh = product_id.qty_available
                if qoh < 1 and self.sale_extra_data:
                    if date_list:
                        # end_date = datetime.strptime(date_list[-1], "%Y-%m-%d")
                        day_range = (date_list[-1] - from_date.date()).days if date_list else 0
                        avg_revenue_day = revenue / day_range if day_range != 0 else 0

                        avg_sale_day = sale_qty / day_range if day_range != 0 else 0
                profit = product_id.lst_price - product_id.standard_price
                # if new_total_in:
                #     total_in_percentage = round((total_in * 100) / new_total_in, 2)
                if new_total_out:
                    total_out_percentage = round((total_out * 100) / new_total_out, 2)
                if new_total_in:
                    new_out_in = round(new_total_out / new_total_in, 2)
                # total_in_percentage = "{} %".format(total_in_percentage)
                # total_out_percentage = "{} %".format(total_out_percentage)
                # forcasted_profit = qoh * profit
                if mto_id in product_id.route_ids.ids or mto_mts_id in product_id.route_ids.ids:
                    make_to_order = "YES"
                else:
                    make_to_order = "NO"
                if product_id.categ_ids:
                    category_list = [category_id.display_name for category_id in product_id.categ_ids]
                else:
                    category_list = [""]
                vendor = product_id.seller_ids and product_id.seller_ids[0].name.name or ""
                if self.filter_value:
                    if self.filter_option == 'qoh':
                        if self.filter_range == 'greater':
                            if not qoh > self.filter_value:
                                continue
                        else:
                            if not qoh < self.filter_value:
                                continue
                    elif self.filter_option == 'sale_qty':
                        if self.filter_range == 'greater':
                            if not sale_qty > self.filter_value:
                                continue
                        else:
                            if not sale_qty < self.filter_value:
                                continue
                    elif self.filter_option == 'revenue':
                        if self.filter_range == 'greater':
                            if not revenue > self.filter_value:
                                continue
                        else:
                            if not revenue < self.filter_value:
                                continue
                    elif self.filter_option == 'profit':
                        if self.filter_range == 'greater':
                            if not profit > self.filter_value:
                                continue
                        else:
                            if not profit < self.filter_value:
                                continue
                    elif self.filter_option == 'total_out':
                        if self.filter_range == 'greater':
                            if not total_out_percentage > self.filter_value:
                                continue
                        else:
                            if not total_out_percentage < self.filter_value:
                                continue
                    elif self.filter_option == 'total_out_create_date':
                        if self.filter_range == 'greater':
                            if not new_total_out > self.filter_value:
                                continue
                        else:
                            if not new_total_out < self.filter_value:
                                continue
                    elif self.filter_option == 'total_cost':
                        if self.filter_range == 'greater':
                            if not qoh > self.filter_value:
                                continue
                        else:
                            if not qoh < self.filter_value:
                                continue
                    else:
                        if self.filter_range == 'greater':
                            if not new_total_in > self.filter_value:
                                continue
                        else:
                            if not new_total_in < self.filter_value:
                                continue

                total_qty_sold += sale_qty

                for category in category_list:
                    worksheet.write(row, 0, serial_no, header2)
                    worksheet.write(row, 1, product_id.display_name, header2)
                    worksheet.write(row, 2, total_days, header2)
                    worksheet.write(row, 3, qoh, header2)
                    worksheet.write(row, 4, vendor, header2)
                    worksheet.write(row, 5, sale_qty, header2)
                    worksheet.write(row, 6, count_sale_order, header2)
                    worksheet.write(row, 7, total_out_percentage, header2)
                    # worksheet.write(row, 7, total_in_percentage, header2)
                    worksheet.write(row, 8, new_total_out, header2)
                    worksheet.write(row, 9, new_total_in, header2)
                    worksheet.write(row, 10, new_out_in, header2)
                    worksheet.write(row, 11, product_id.lst_price, header2)
                    worksheet.write(row, 12, product_id.standard_price, header2)
                    worksheet.write(row, 13, revenue, header2)
                    worksheet.write(row, 14, product_id.standard_price * qoh, header2)
                    worksheet.write(row, 15, profit, header2)
                    worksheet.write(row, 16, make_to_order, header2)
                    worksheet.write(row, 17, category, header2)
                    worksheet.write(row, 18, supplier_type_value, header2)
                    col = 18
                    if self.average_sale_price:
                        col += 1
                        worksheet.write(row, col, total_avg_sale_price, header2)
                        col += 1
                        worksheet.write(row, col, total_avg_sale_price, header2)
                    if self.sale_extra_data:
                        col += 1
                        worksheet.write(row, col, avg_sale_day, header2)
                        col += 1
                        worksheet.write(row, col, avg_revenue_day, header2)
                        col += 1
                        worksheet.write(row, col, max(sale_per_day) if sale_per_day else 0, header2)
                        col += 1
                        worksheet.write(row, col, min(sale_per_day) if sale_per_day else 0, header2)

                    row += 1

                serial_no += 1
            row += 1
            worksheet.write(row, 4, "Total QTY Sold", header4)
            worksheet.write(row, 5, total_qty_sold, header2)

        fp = BytesIO()
        workbook.save(fp)
        fp.seek(0)
        file_new = base64.encodebytes(fp.read())
        fp.close()
        self.write({'data': file_new, 'file_name': "hp_stock_report"})
        if from_cron == "Weekly":
            # email code starts
            cron_emails_id = self.env["cron.emails"].search([("report_type", "=", "hp_stock_report")],
                                                            limit=1)
            if cron_emails_id:
                attachment_name = "HP Stock Report {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))
                attachment_id = self.env['ir.attachment'].create({
                    'name': attachment_name,
                    'type': 'binary',
                    'datas': file_new,
                    'datas_fname': attachment_name + '.xls',
                    'store_fname': attachment_name,
                    'res_model': self._name,
                    'res_id': self.id,
                    'mimetype': 'application/x-xls'
                })
                # icpSudo = self.env['ir.config_parameter'].sudo()  # it is given all access
                # email = icpSudo.get_param('eg_product_supplier_report.email_id', default="")

                subject = "{} HP Stock Report".format(from_cron)

                body_html = "<p>Hello</p></b> Please check {} HP Stock Report for duration {}.</b><p>Thanks</p>".format(
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
            return {'type': "ir.actions.act_url",
                    'url': 'web/content/?model=hp.stock.report&download=true&field=data&id=%s&filename=%s - %s.xls' % (
                        self.id, self.file_name, datetime.now().strftime("%Y-%m-%d")),
                    'target': 'self'}

    @api.multi
    def send_report_by_email(self):
        from_date = date.today() - timedelta(days=7)
        to_date = date.today()
        new_wizard = self.create({"from_date": from_date,
                                  "to_date": to_date}).generate_stock_product_report(from_cron="Weekly")

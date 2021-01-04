import base64
import datetime
from datetime import datetime, timedelta
from io import BytesIO

from dateutil.relativedelta import relativedelta

from odoo import models, fields, api
from odoo.exceptions import Warning, ValidationError
from odoo.http import request

try:
    import xlwt
    from xlwt import Borders
except ImportError:
    xlwt = None


class TopGrowingProductReportEpt(models.TransientModel):
    _name = 'top.growing.product.report.ept'

    datas = fields.Binary('File')

    product_ids = fields.Many2many("product.product", "report_top_growing_product_rel", "wizard_id", "report_id",
                                   "Products")
    product_category_ids = fields.Many2many("product.category", "report_top_growing_category_rel", "wizard_id",
                                            "category_id", "Product Categories")
    from_date = fields.Date(string='From Date')
    to_date = fields.Date(string='To Date')
    is_include_default_days = fields.Boolean(string="Is Include Default Days?")
    default_days = fields.Integer(string="Default Days")
    period_to_check_in = fields.Selection([('current', 'Current Year'),
                                           ('past', 'Past Year')],
                                          string='Period To Check In ')
    vendor_id = fields.Many2one("res.partner", string="Vendors")

    @api.multi
    def view_onscreen_report(self):
        product_obj = self.env['product.product']
        domain = [('type', '!=', 'service')]
        report_top_growing_product_obj = self.env['report.top.growing.product.ept']
        from_date = self.from_date
        to_date = self.to_date
        date_1 = datetime.strptime(str(from_date), '%Y-%m-%d')
        date_2 = datetime.strptime(str(to_date), "%Y-%m-%d")
        if date_1 > datetime.now():
            raise ValidationError("Fromdate is not greater than Today")
        elif date_2 > datetime.now():
            raise ValidationError("Todate is not greater than Today")
        elif not (date_1 <= date_2):
            raise ValidationError("Fromdate is not greater than Todate")

        if self.product_ids:
            all_product_ids = self.product_ids
        else:
            all_product_ids = product_obj.search(domain) or []

        if self.product_category_ids:
            product_category_ids = self.product_category_ids
        else:
            product_category_ids = self.env['product.category'].search([]) or []

        if not all_product_ids or not product_category_ids:
            raise ValidationError("No Records Found !!!")

        product_ids = '(' + str(all_product_ids.ids).strip('[]') + ')'
        categ_ids = '(' + str(product_category_ids.ids).strip('[]') + ')'

        past_from = (datetime.strptime(self.from_date, '%Y-%m-%d') - relativedelta(years=1)).date()
        past_to = (datetime.strptime(self.to_date, '%Y-%m-%d') - relativedelta(years=1)).date()

        if self.period_to_check_in == 'current':
            from_date = self.from_date
            to_date = self.to_date
            query = self.prepare_query(product_ids, categ_ids, str(from_date), str(to_date))
        else:
            query = self.prepare_query(product_ids, categ_ids, str(past_from), str(past_to))

        report_top_growing_product_obj.get_top_growing_product_report(query)
        search_view = self.env.ref('top_growing_product_ept.view_report_top_growing_product_report_ept_search').id
        tree_view = self.env.ref('top_growing_product_ept.view_report_top_growing_product_report_ept_tree').id
        pivot_view = self.env.ref('top_growing_product_ept.view_report_top_growing_product_report_ept_pivot').id
        return {
            'name': 'Top Growing Product',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'kanban',
            'res_model': 'report.top.growing.product.ept',
            'search_view_id': search_view,
            'views': [(pivot_view, 'pivot'), (tree_view, 'tree')],
            'view_id': pivot_view,
            'target': 'current',
        }

    @api.multi
    def print_top_growing_report_xls(self):
        """ Download xls file and also provide product wise ,categories wise, 
            and both product and categorie wise xls,
            
            When data not available then send a warning No Data Available
        """
        product_obj = self.env['product.product']
        active_id = self.ids[0]

        today = datetime.now().strftime("%Y-%m-%d")
        f_name = 'Top Growing Products' + ' ' + today

        domain = [('type', '!=', 'service')]
        # need to add vendor domain if selected
        if self.vendor_id:
            supplierifo_ids = self.env['product.supplierinfo'].search([('name', '=', self.vendor_id.id)])
            product_tmpl_ids = supplierifo_ids.mapped('product_tmpl_id')
            product_ids = product_tmpl_ids.mapped('product_variant_ids')
            domain.append(('id', 'in', product_ids.ids))
        from_date = self.from_date
        to_date = self.to_date
        date_1 = datetime.strptime(str(from_date), '%Y-%m-%d')
        date_2 = datetime.strptime(str(to_date), "%Y-%m-%d")
        if date_1 > datetime.now():
            raise ValidationError("Fromdate is not greater than Today")
        elif date_2 > datetime.now():
            raise ValidationError("Todate is not greater than Today")
        elif not (date_1 <= date_2):
            raise ValidationError("Fromdate is not greater than Todate")

        if self.product_ids:
            product_ids = self.product_ids
        else:
            product_ids = product_obj.search(domain) or []

        if self.product_category_ids:
            product_category_ids = self.product_category_ids
        else:
            # product_category_ids = self.env['product.category'].search([]) or []

            product_category_ids = self.env['sale.order.line'].search(
                [('product_id.type', '=', 'product'), ('order_id.state', 'not in', ['draft', 'cancel'])]).mapped(
                'product_id').mapped('categ_id')

        if not product_ids or not product_category_ids:
            raise ValidationError("No Records Found !!!")

        check_data, categories, products = self.generate_top_growing_product_report(today, product_ids,
                                                                                    product_category_ids)
        if not check_data:
            raise Warning("No Data Available")

        if self.datas:
            return {
                'type': 'ir.actions.act_url',
                'url': 'web/content/?model=top.growing.product.report.ept&download=true&field=datas&id=%s&filename=%s.xls' % (
                    active_id, f_name),
                'target': 'self',
            }

    @api.multi
    def generate_top_growing_product_report(self, today, all_product_ids, product_category_ids):
        data_dict = {}
        workbook, header_bold, body_style, style, header_title, cell_string_style, cell_number_style = self.create_sheet()
        workbook, worksheet_all_category = self.all_category_headings(workbook, header_bold)
        data_dict, prodcut_data_dict = self.get_data(today, all_product_ids, product_category_ids, data_dict)
        self.print_all_inv_data(prodcut_data_dict, worksheet_all_category, body_style)
        workbook, new_workbook, row_data = self.add_headings(product_category_ids, workbook, header_bold)
        if not data_dict:
            return False, product_category_ids, all_product_ids

        self.print_product_data(data_dict, row_data, new_workbook, cell_string_style, cell_number_style)
        fp = BytesIO()
        workbook.save(fp)
        fp.seek(0)
        sale_file = base64.encodebytes(fp.read())
        fp.close()
        self.write({'datas': sale_file})
        return True, product_category_ids, all_product_ids

    @api.multi
    def print_all_inv_data(self, prodcut_data_dict, worksheet_all_category, body_style):
        row = 2
        column = 0
        for product_id, product_data in prodcut_data_dict.items():
            worksheet_all_category.row(row).height = 350
            worksheet_all_category.write(row, column, row - 1, body_style)
            worksheet_all_category.write(row, column + 1, product_data.get('default_code') or '-', body_style)
            worksheet_all_category.write(row, column + 2, product_data.get('product_name'), body_style)
            worksheet_all_category.write(row, column + 3, product_data.get('category'), body_style)
            worksheet_all_category.write(row, column + 4, product_data.get('avg_sale_price'), body_style)
            worksheet_all_category.write(row, column + 5, product_data.get('avg_purchase_price'), body_style)
            worksheet_all_category.write(row, column + 6, product_data.get('current_stock'), body_style)
            worksheet_all_category.write(row, column + 7, product_data.get('total_sale'), body_style)
            worksheet_all_category.write(row, column + 8, product_data.get('total_purchase'), body_style)
            worksheet_all_category.write(row, column + 9, product_data.get('average_sale'), body_style)
            worksheet_all_category.write(row, column + 10, product_data.get('selected_period_sales'), body_style)
            worksheet_all_category.write(row, column + 11, product_data.get('growth_ratio'), body_style)
            worksheet_all_category.write(row, column + 12, product_data.get('rack_location'), body_style)

            row += 1
        return True

        return True

    @api.multi
    def create_sheet(self):
        """
        create a sheet in sheet set color, border, font,etc... 
        """
        workbook = xlwt.Workbook()
        borders = Borders()
        header_border = Borders()
        header_title_border = Borders()
        ware_or_loc_border = Borders()
        header_border.left, header_border.right, header_border.top, header_border.bottom = Borders.THIN, Borders.THIN, Borders.THIN, Borders.THICK
        header_title_border.left, header_title_border.right, header_title_border.top, header_title_border.bottom = Borders.THIN, Borders.THIN, Borders.THIN, Borders.THICK
        ware_or_loc_border.left, ware_or_loc_border.right, ware_or_loc_border.top, ware_or_loc_border.bottom = Borders.THIN, Borders.THIN, Borders.THIN, Borders.THICK
        borders.left, borders.right, borders.top, borders.bottom = Borders.THIN, Borders.THIN, Borders.THIN, Borders.THIN
        header_bold = xlwt.easyxf(
            "font: bold on, height 250; pattern: pattern solid, fore_colour gray25;alignment: horizontal center ,vertical center")
        header_bold.borders = header_border
        body_style = xlwt.easyxf("font: height 200; alignment: horizontal center")
        style = xlwt.easyxf(
            "font: height 210, bold True; alignment: horizontal center,vertical center;borders: top medium,right medium,bottom medium,left medium")
        body_style.borders = borders

        header_title = xlwt.easyxf(
            "font: bold on, height 315; pattern: pattern solid, fore_colour ice_blue;alignment: horizontal center ,vertical center")
        header_title.borders = header_title_border

        xlwt.add_palette_colour("light_blue_21", 0x25)
        workbook.set_colour_RGB(0x25, 179, 255, 240)
        cell_string_style = xlwt.easyxf(
            "font: height 200, name Arial; align: horiz left, vert center;  pattern: pattern solid, fore_colour light_blue_21;  borders: top thin,right thin,bottom thin,left thin")

        xlwt.add_palette_colour("light_blue_21", 0x25)
        workbook.set_colour_RGB(0x25, 179, 255, 240)
        cell_number_style = xlwt.easyxf(
            "font: height 200, name Arial; align: horiz right, vert center;  pattern: pattern solid, fore_colour light_blue_21;  borders: top thin,right thin,bottom thin,left thin")
        return workbook, header_bold, body_style, style, header_title, cell_string_style, cell_number_style

    @api.multi
    def add_headings(self, categories_or_warehouses, workbook, header_bold):
        """
            put heading in xls file and ganarate a xls file which name is categorie name
        
        """
        row_data = {}
        sheet_data = {}

        for record in categories_or_warehouses:
            record.new_workbook = workbook.add_sheet(" %s" % (record.display_name), cell_overwrite_ok=True)
            record.new_workbook.write_merge(0, 0, 0, 11, "Top Growing Products", header_bold)
            record.new_workbook.row(0).height_mismatch = True
            record.new_workbook.row(0).height = 350
            record.new_workbook.row(1).height_mismatch = True
            record.new_workbook.row(1).height = 350
            record.new_workbook.col(0).width = 1000
            record.new_workbook.col(1).width = 4000
            record.new_workbook.col(2).width = 8000
            record.new_workbook.col(3).width = 5500
            record.new_workbook.col(4).width = 3500
            record.new_workbook.col(5).width = 3500
            record.new_workbook.col(6).width = 3500
            record.new_workbook.col(7).width = 3500
            record.new_workbook.col(8).width = 3500
            record.new_workbook.col(9).width = 3500
            record.new_workbook.col(10).width = 3500
            record.new_workbook.col(11).width = 3500

            record.new_workbook.write(1, 0, 'No', header_bold)
            record.new_workbook.write(1, 1, 'SKU', header_bold)
            record.new_workbook.write(1, 2, 'Name', header_bold)
            record.new_workbook.write(1, 3, 'Category', header_bold)
            record.new_workbook.write(1, 4, 'Average Sale Price', header_bold)
            record.new_workbook.col(4).width = (len('Average Sale Price') * 367)
            record.new_workbook.write(1, 5, 'Average Cost Price', header_bold)
            record.new_workbook.col(5).width = (len('Average Cost Price') * 367)
            record.new_workbook.write(1, 6, 'Current Stock', header_bold)
            record.new_workbook.col(6).width = (len('Current Stock') * 367)
            record.new_workbook.write(1, 8, 'Total purchase', header_bold)
            record.new_workbook.col(8).width = (len('Total purchase') * 367)
            record.new_workbook.write(1, 7, 'Total sales', header_bold)
            record.new_workbook.col(7).width = (len('Total sales') * 367)
            record.new_workbook.write(1, 9, 'Last Period Sales', header_bold)
            record.new_workbook.col(9).width = (len('Last Period Sales') * 367)
            record.new_workbook.write(1, 10, 'Selected Period Sales', header_bold)
            record.new_workbook.col(10).width = (len('Selected Period Sales') * 367)
            record.new_workbook.write(1, 11, 'Growth Ratio', header_bold)
            record.new_workbook.col(11).width = (len('Growth Ratio') * 367)
            record.new_workbook.write(1, 12, 'Rack Location', header_bold)
            record.new_workbook.col(12).width = (len('Rack Location') * 367)
            record.new_workbook.set_panes_frozen(True)
            record.new_workbook.set_horz_split_pos(2)
            # #Get categories wise worksheet
            sheet_data.update({record.id: record.new_workbook})
            row_data.update({record.new_workbook: 2})
        return workbook, sheet_data, row_data

    @api.multi
    def prepare_query(self, product_ids, categ_ids, from_date, todate):
        from_date_add_one = datetime.strptime(from_date, '%Y-%m-%d') + timedelta(days=0)
        from_date_add_one_str = str(from_date_add_one.strftime('%Y-%m-%d') + ' 00:00:00')
        todate_add_one = datetime.strptime(todate, '%Y-%m-%d') + timedelta(days=0)
        todate_add_one_for_previous = datetime.strptime(str(todate), '%Y-%m-%d') + timedelta(days=1)
        todate_add_one_str = str(todate_add_one.strftime('%Y-%m-%d') + ' 23:59:59')

        d0 = todate_add_one_for_previous
        d1 = datetime.strptime(from_date, '%Y-%m-%d') + timedelta(days=0)
        delta = d1 - d0
        no_of_days = abs(delta.days)
        date_of_privious_piriod_start = str(datetime.strptime(from_date, '%Y-%m-%d') - timedelta(days=no_of_days))

        date_of_privious_piriod_end = datetime.strptime(from_date, '%Y-%m-%d') - relativedelta(days=1)
        date_of_privious_piriod_end_str = str(date_of_privious_piriod_end.strftime('%Y-%m-%d') + ' 23:59:59')

        past_from_date_add_one = datetime.strptime(from_date, '%Y-%m-%d') + relativedelta(years=1)
        past_from_date_add_one_str = str(past_from_date_add_one.strftime('%Y-%m-%d') + ' 00:00:00')
        past_todate_add_one = datetime.strptime(todate, '%Y-%m-%d') + relativedelta(years=1)
        past_todate_add_one_for_previous = datetime.strptime(str(todate), '%Y-%m-%d') - relativedelta(years=0)
        past_todate_add_one_str = str(past_todate_add_one.strftime('%Y-%m-%d') + ' 23:59:59')

        p0 = past_todate_add_one_for_previous
        p1 = datetime.strptime(from_date, '%Y-%m-%d') - relativedelta(years=1)
        delta = p1 - p0
        no_of_days = abs(delta.days)
        past_date_of_privious_piriod_start = str(datetime.strptime(from_date, '%Y-%m-%d') - relativedelta(years=0))
        past_date_of_privious_piriod_end = datetime.strptime(todate, '%Y-%m-%d') - relativedelta(years=0)
        past_date_of_privious_piriod_end_str = str(past_date_of_privious_piriod_end.strftime('%Y-%m-%d') + ' 23:59:59')
        if self.period_to_check_in == 'current':
            args = (from_date_add_one_str, todate_add_one_str,
                    from_date_add_one_str, todate_add_one_str,
                    from_date_add_one_str, todate_add_one_str,
                    date_of_privious_piriod_start, date_of_privious_piriod_end_str,
                    from_date_add_one_str, todate_add_one_str,
                    from_date_add_one_str, todate_add_one_str,
                    from_date_add_one_str, todate_add_one_str,
                    product_ids, categ_ids)
        else:
            args = (past_from_date_add_one_str, past_todate_add_one_str,
                    past_from_date_add_one_str, past_todate_add_one_str,
                    past_from_date_add_one_str, past_todate_add_one_str,
                    past_date_of_privious_piriod_start, past_date_of_privious_piriod_end_str,
                    past_from_date_add_one_str, past_todate_add_one_str,
                    past_from_date_add_one_str, past_todate_add_one_str,
                    past_from_date_add_one_str, past_todate_add_one_str,
                    product_ids, categ_ids)
        qry = """    
            Select 
            ROW_NUMBER() over() AS id,
            default_code,
            product.product_id,
            product_name,
            categ_id,
            category,
            COALESCE(round(sale.previous_period_sale,2),0) as past_period_sales,
            COALESCE(round(sale.current_period_sale,2),0) as current_period_sales,
            COALESCE(round(sale.total_sale_pro,2),0) as total_sale,
            COALESCE(round(sale.average_sale_price,2),0) as average_sale_price,
            COALESCE(round(purchase.purchase,2),0) as Total_Purchase,
            COALESCE(round(purchase.average_purchase_price,2),0) as average_cost_price,
            COALESCE(current_stock,0) as current_stock, 
            COALESCE(round(sale.sale_pro_avg,2),0) as average_sale,
            CASE WHEN (sale.previous_period_sale != 0 AND sale.current_period_sale != 0) 
                        THEN COALESCE(round((((sale.current_period_sale-sale.previous_period_sale)*100)/sale.previous_period_sale),2),0) 
                 WHEN (sale.previous_period_sale is NULL AND sale.current_period_sale != 0) 
                        THEN '100'
                 WHEN (sale.previous_period_sale != 0 AND sale.current_period_sale is NULL)
                        THEN '-100'
            ELSE
                 '0'
            END as growth_ratio
            from
            (
            select p.id as product_id,categ.id as categ_id,product_tmpl_id,p.default_code, categ.name as category, tmpl.name as product_name
            from product_product p 
                Inner join product_template tmpl on tmpl.id = p.product_tmpl_id
                Inner Join product_category categ on categ.id = tmpl.categ_id
            where p.active = true and tmpl.active = true
            )product
            Left Join
            (
            Select 
            product_id, 
            sum(product_uom_qty) filter (where confirmation_date BETWEEN '%s' and '%s') as total_sale_pro , 
            avg(price_unit) filter (where confirmation_date BETWEEN '%s' and '%s') as average_sale_price,
            sum(product_uom_qty)filter ( where confirmation_date BETWEEN '%s' and '%s') as current_period_sale,
            sum(product_uom_qty)filter ( where confirmation_date BETWEEN '%s' and '%s') as previous_period_sale,
            sum(product_uom_qty)filter ( where confirmation_date BETWEEN '%s' and '%s') as sale_pro_avg
            
            from sale_order_line line
            Inner Join sale_order so on line.order_id=so.id  
            Inner Join product_product p on p.id = line.product_id
            where so.state !='cancel' and so.state !='draft'
            group by product_id
            
            ) sale on sale.product_id = product.product_id
            Left join
            (
            Select product_id, 
            sum(product_qty) filter (where date_order BETWEEN '%s' and '%s') as purchase,
            avg(price_unit) filter (where date_order BETWEEN '%s' and '%s') as average_purchase_price 
            from purchase_order_line
            Inner Join purchase_order po on po.id = purchase_order_line.order_id 
            Inner Join product_product p on p.id = purchase_order_line.product_id
            group by product_id
            )purchase on purchase.product_id = product.product_id
            Left Join
            (
            select sum(quantity) as current_stock,product_id from stock_quant sq 
                left join stock_location sl on sq.location_id=sl.id
            where sl.usage = 'internal'
            group by product_id
            ) stock_qu on stock_qu.product_id=product.product_id
            where product.product_id in %s and categ_id in %s order by growth_ratio desc
            """ % args
        return qry

    @api.model
    def get_data(self, today, all_product_ids, product_category_ids, data_dict):
        """
            Collect data from qry and return data_dict
        """
        product_categ_obj = self.env['product.category']
        date_filter = ""
        date_filter = date_filter + 'and date::date <=' + "'"
        product_ids = '(' + str(all_product_ids.ids).strip('[]') + ')'
        categ_ids = '(' + str(product_category_ids.ids).strip('[]') + ')'
        past_from = (datetime.strptime(self.from_date, '%Y-%m-%d') - relativedelta(years=1)).date()
        past_to = (datetime.strptime(self.to_date, '%Y-%m-%d') - relativedelta(years=1)).date()

        if self.period_to_check_in == 'current':
            from_date = self.from_date
            to_date = self.to_date
            qry = self.prepare_query(product_ids, categ_ids, str(from_date), str(to_date))
        else:
            qry = self.prepare_query(product_ids, categ_ids, str(past_from), str(past_to))

        # print(qry)
        self._cr.execute(qry)
        execute_qry = self._cr.dictfetchall()
        prodcut_data_dict = {}
        for record in execute_qry:
            product_id = self.env['product.product'].browse(record.get('product_id'))
            categ_id = product_categ_obj.search([('id', '=', record.get('categ_id', False))], limit=1)
            prodcut_data_dict.update({record.get('product_id'): {
                'default_code': record.get('default_code'),
                'product_name': record.get('product_name'),
                'category': record.get('category'),
                'avg_sale_price': int(round(record.get('average_sale_price', 0))),
                'avg_purchase_price': int(round(record.get('average_cost_price', 0))),
                'current_stock': int(round(record.get('current_stock', 0))),
                'total_sale': int(round(record.get('total_sale', 0))),
                'total_purchase': int(round(record.get('total_purchase', 0))),
                'average_sale': int(round(record.get('past_period_sales', 0))),
                'selected_period_sales': int(round(record.get('current_period_sales', 0))),
                'growth_ratio': round(record.get('growth_ratio', 0), 2) if record.get('growth_ratio') else 0,
                'rack_location': product_id.rack
                # round(growth_ratio,2)
            }})

            if categ_id:
                if data_dict.get(categ_id.id):
                    data_dict.get(categ_id.id).append({'id': record.get('id', False),
                                                       'default_code': record.get('default_code'),
                                                       'product_name': record.get('product_name'),
                                                       'category': record.get('category'),
                                                       'avg_sale_price': int(
                                                           round(record.get('average_sale_price', 0))),
                                                       'avg_purchase_price': int(
                                                           round(record.get('average_cost_price', 0))),
                                                       'current_stock': int(round(record.get('current_stock', 0))),
                                                       'total_sale': int(round(record.get('total_sale', 0))),
                                                       'total_purchase': int(round(record.get('total_purchase', 0))),
                                                       'average_sale': int(round(record.get('past_period_sales', 0))),
                                                       'selected_period_sales': int(
                                                           round(record.get('current_period_sales', 0))),
                                                       'growth_ratio': round(record.get('growth_ratio', 0),
                                                                             2) if record.get('growth_ratio') else 0,
                                                       'rack_location': product_id.rack,
                                                       # round(growth_ratio,2)
                                                       })
                else:
                    data_dict.update({categ_id.id: [{'id': record.get('id', False),
                                                     'default_code': record.get('default_code'),
                                                     'product_name': record.get('product_name'),
                                                     'category': record.get('category'),
                                                     'avg_sale_price': int(round(record.get('average_sale_price', 0))),
                                                     'avg_purchase_price': int(
                                                         round(record.get('average_cost_price', 0))),
                                                     'current_stock': int(round(record.get('current_stock', 0))),
                                                     'total_sale': int(round(record.get('total_sale', 0))),
                                                     'total_purchase': int(round(record.get('total_purchase', 0))),
                                                     'average_sale': int(round(record.get('past_period_sales', 0))),
                                                     'selected_period_sales': int(
                                                         round(record.get('current_period_sales', 0))),
                                                     'growth_ratio': round(record.get('growth_ratio', 0),
                                                                           2) if record.get(
                                                         'growth_ratio') else 0,
                                                     'rack_location': product_id.rack, }]})  # round(growth_ratio)

        return data_dict, prodcut_data_dict

    def all_category_headings(self, workbook, header_bold):
        worksheet_all_category = workbook.add_sheet('All Category', cell_overwrite_ok=True)
        worksheet_all_category.write_merge(0, 0, 0, 11, "Top Growing Products", header_bold)
        worksheet_all_category.row(0).height_mismatch = True
        worksheet_all_category.row(0).height = 350
        worksheet_all_category.row(1).height_mismatch = True
        worksheet_all_category.row(1).height = 350
        worksheet_all_category.col(0).width = 1000
        worksheet_all_category.col(1).width = 4000
        worksheet_all_category.col(2).width = 8000
        worksheet_all_category.col(3).width = 5500
        worksheet_all_category.col(4).width = 3500
        worksheet_all_category.col(5).width = 3500
        worksheet_all_category.col(6).width = 3500
        worksheet_all_category.col(7).width = 3500
        worksheet_all_category.col(8).width = 3500
        worksheet_all_category.col(9).width = 3500
        worksheet_all_category.col(10).width = 3500
        worksheet_all_category.col(11).width = 3500
        worksheet_all_category.write(1, 0, 'No', header_bold)
        worksheet_all_category.write(1, 1, 'SKU', header_bold)
        worksheet_all_category.write(1, 2, 'Name', header_bold)
        worksheet_all_category.write(1, 3, 'Category', header_bold)
        worksheet_all_category.write(1, 4, 'Average Sale Price', header_bold)
        worksheet_all_category.col(4).width = (len('Average Sale Price') * 367)
        worksheet_all_category.write(1, 5, 'Average Cost Price', header_bold)
        worksheet_all_category.col(5).width = (len('Average Cost Price') * 367)
        worksheet_all_category.write(1, 6, 'Current Stock', header_bold)
        worksheet_all_category.col(6).width = (len('Current Stock') * 367)
        worksheet_all_category.write(1, 8, 'Total purchase', header_bold)
        worksheet_all_category.col(8).width = (len('Total purchase') * 367)
        worksheet_all_category.write(1, 7, 'Total sales', header_bold)
        worksheet_all_category.col(7).width = (len('Total sales') * 367)
        worksheet_all_category.write(1, 9, 'Last Period Sales', header_bold)
        worksheet_all_category.col(9).width = (len('Last Period Sales') * 367)
        worksheet_all_category.write(1, 10, 'Selected Period Sales', header_bold)
        worksheet_all_category.col(10).width = (len('Selected Period Sales') * 367)
        worksheet_all_category.write(1, 11, 'Growth Ratio', header_bold)
        worksheet_all_category.col(11).width = (len('Growth Ratio') * 367)
        worksheet_all_category.write(1, 12, 'Rack Location', header_bold)
        worksheet_all_category.col(12).width = (len('Rack Location') * 367)
        worksheet_all_category.set_panes_frozen(True)
        worksheet_all_category.set_horz_split_pos(2)

        return workbook, worksheet_all_category

    @api.multi
    def print_product_data(self, data_dict, row_data, new_workbook, cell_string_style, cell_number_style):
        """
          print product data in row
        """
        for categ_id, data_details in data_dict.items():
            for single_data in data_details:
                row = row_data[new_workbook[categ_id]]
                new_workbook[categ_id].row(row).height = 350
                new_workbook[categ_id].write(row, 0, single_data.get('id'))
                new_workbook[categ_id].row(row).height = 300
                new_workbook[categ_id].write(row, 1, single_data.get('default_code'))
                new_workbook[categ_id].row(row).height = 300
                new_workbook[categ_id].write(row, 2, single_data.get('product_name'))
                new_workbook[categ_id].row(row).height = 300
                new_workbook[categ_id].write(row, 3, single_data.get('category'))
                new_workbook[categ_id].row(row).height = 300
                new_workbook[categ_id].write(row, 4, single_data.get('avg_sale_price'))
                new_workbook[categ_id].row(row).height = 300
                new_workbook[categ_id].write(row, 5, single_data.get('avg_purchase_price'))
                new_workbook[categ_id].row(row).height = 300
                new_workbook[categ_id].write(row, 6, single_data.get('current_stock'))
                new_workbook[categ_id].row(row).height = 300
                new_workbook[categ_id].write(row, 7, single_data.get('total_sale'))
                new_workbook[categ_id].row(row).height = 300
                new_workbook[categ_id].write(row, 8, single_data.get('total_purchase'))
                new_workbook[categ_id].row(row).height = 300
                new_workbook[categ_id].write(row, 9, single_data.get('average_sale'))
                new_workbook[categ_id].row(row).height = 300
                new_workbook[categ_id].write(row, 10, single_data.get('selected_period_sales'))
                new_workbook[categ_id].row(row).height = 300
                new_workbook[categ_id].write(row, 11, single_data.get('growth_ratio'))
                new_workbook[categ_id].row(row).height = 300
                new_workbook[categ_id].write(row, 12, single_data.get('rack_location'))
                new_workbook[categ_id].row(row).height = 300
                row += 1
                row_data.update({new_workbook[categ_id]: row})
        return True

    @api.model
    def auto_generator_export_stockinfo_report(self):
        """
            collect data for pdf report in that first condition return only products wise data when only product select
            second condition return product and product categories wise data when both select third condition return categories wise data when only product categories select
            else ganarete all data into pdf

        """
        report_list = []
        all_report_list = []
        all_report_data = {}
        report_data = {}
        data_dict = {}
        product_obj = self.env['product.product']
        product_cate_obj = self.env['product.category']
        today = datetime.now().strftime("%Y-%m-%d")
        if self.product_ids:
            all_product_ids = self.product_ids
        else:
            all_product_ids = product_obj.search([('type', '!=', 'service')]) or []

        if self.product_category_ids:
            product_category_ids = self.product_category_ids
        else:
            product_category_ids = product_cate_obj.search([]) or []

        if not all_product_ids or not product_category_ids:
            raise ValidationError("No Records Found !!!")

        data_dict, prodcut_data_dict = self.get_data(today, all_product_ids, product_category_ids, data_dict)
        # print(prodcut_data_dict)
        count = 0
        for product, data in prodcut_data_dict.items():
            count += 1
            report_data = {
                'no': count,
                'product_name': data.get('product_name') or '-',
                'default_code': data.get('default_code') or '-',
                'categories': data.get('category') or '-',
                'current_stock': data.get('current_stock') or '0',
                'total_sale': data.get('total_sale') or '0',
                'average_sale_price': data.get('avg_sale_price') or '0',
                'average_cost_price': data.get('avg_purchase_price') or '0',
                'average_sale': data.get('average_sale') or '0',
                'selected_period_sales': data.get('selected_period_sales') or '0',
                'total_purchase': data.get('total_purchase') or '0',
                'growth_ratio': data.get('growth_ratio') or '0',
                'rack_location': data.get('rack_location')
            }
            all_report_list.append(report_data)

        for categ_id, data_details in data_dict.items():
            count = 0
            for single_data in data_details:
                count += 1
                all_report_data = {
                    'no': count,
                    'product_name': single_data.get('product_name') or '-',
                    'default_code': single_data.get('default_code') or '-',
                    'categories': single_data.get('category') or '-',
                    'current_stock': single_data.get('current_stock') or '0',
                    'total_sale': single_data.get('total_sale') or '0',
                    'average_sale_price': single_data.get('avg_sale_price') or '0',
                    'average_cost_price': single_data.get('avg_purchase_price') or '0',
                    'average_sale': single_data.get('average_sale') or '0',
                    'selected_period_sales': single_data.get('selected_period_sales') or '0',
                    'total_purchase': single_data.get('total_purchase') or '0',
                    'growth_ratio': single_data.get('growth_ratio') or '0',
                    'rack_location': data.get('rack_location')
                }
                report_list.append(all_report_data)

        return report_list, all_report_list

    @api.multi
    def print_top_growing_report_pdf(self):
        """
            call action action_report_top_growing_product which in
            view_top_growing_product_report_ept_pdf.xml
            in that pass data and data get report_list which return in
            auto_generator_export_stockinfo_report()
        """
        from_date = self.from_date
        to_date = self.to_date
        date_1 = datetime.strptime(str(from_date), '%Y-%m-%d')
        date_2 = datetime.strptime(str(to_date), "%Y-%m-%d")
        if date_1 > datetime.now():
            raise ValidationError("Fromdate is not greater than Today")
        elif date_2 > datetime.now():
            raise ValidationError("Todate is not greater than Today")
        if not (date_1 <= date_2):
            raise ValidationError("Fromdate is not greater then Todate")

        report_list, prodcut_data_dict = self.auto_generator_export_stockinfo_report()
        if not report_list:
            raise ValidationError("No record Found !!!")
        pdf = request.env.ref('top_growing_product_ept.action_report_top_growing_product').with_context(
            {'data': report_list, 'final_data': prodcut_data_dict, 'landscape': True}).render_qweb_pdf(
            res_ids=self.ids)[0]
        self.datas = base64.b64encode(pdf)
        file_name = 'top_growing_products.pdf'
        return {
            'type': 'ir.actions.act_url',
            'url': 'web/content/?model=top.growing.product.report.ept&field=datas&download=true&id=%s&filename=%s' % (
                self.id, file_name),
            'target': 'new',
        }

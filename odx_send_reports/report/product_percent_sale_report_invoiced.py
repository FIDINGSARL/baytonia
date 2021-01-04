from odoo import api, models

from datetime import date, timedelta, datetime

class MtoReport(models.AbstractModel):
    _name = 'report.odx_send_reports.invoiced_qty_template'


    @api.multi
    def get_report_values(self, docids, data=None):
        from_date = str(date.today() - timedelta(days=7))
        to_date = str(date.today())

        query_picking = """select pt.name as product_name,pp.id as product_id ,sum(sl.qty_invoiced) as sale_qty, sum(sl.price_unit * sl.qty_invoiced) as profit from sale_order_line sl
                                                        inner join product_product pp on pp.id = sl.product_id
                                                        inner join product_template pt on pt.id = pp.product_tmpl_id
                                                        inner join sale_order so on so.id = sl.order_id
                                                        where
                                                        so.confirmation_date::date between '""" + \
                        str(from_date) + """' and '""" + str(to_date) + """'  group by pt.name, pp.id"""

        self.env.cr.execute(query_picking)
        results = self.env.cr.dictfetchall()
        total_sale = 0
        total_profit_report = 0
        high_sale = 0
        high_profit = 0
        serial_no = 0

        for result in results:
            if result['sale_qty'] > high_sale:
                high_sale = result['sale_qty']
            total_sale += result['sale_qty']

            if result['profit'] > high_profit:
                high_profit = result['profit']
            total_profit_report += result['profit']

        for product_dict in results:
            serial_no = serial_no +1
            product_id = self.env["product.product"].search([("id", "=", product_dict.get("product_id"))], limit=1)
            product_dict['image'] = product_id.image_small
            product_dict['serial_no'] = serial_no

            if high_sale:
                product_dict['sale_percentage'] = round((product_dict.get("sale_qty") * 100) / high_sale, 2)
            if total_sale:
                product_dict['total_sale_percentage'] = round((product_dict.get("sale_qty") * 100) / total_sale, 2)
            if total_profit_report:
                product_dict['total_profit_percentage'] = round(
                    (product_dict.get("profit") * 100) / total_profit_report, 2)

            if high_profit:
                product_dict['profit_percentage'] = round((product_dict.get("profit") * 100) / high_profit, 2)



        return {
            'data': results,
            'date_from': from_date,
            'date_to': to_date
        }
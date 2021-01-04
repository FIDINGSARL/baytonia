from odoo import api, models

from datetime import date, timedelta, datetime

class MtoReport(models.AbstractModel):
    _name = 'report.odx_send_reports.stock_product_template'


    @api.multi
    def get_report_values(self, docids, data=None):
        from_date = str(date.today() - timedelta(days=7))
        to_date = str(date.today())


        results = []
        serial_no = 0
        product_ids = self.env["product.product"].search([("qty_available", ">", 0.0)])
        mto_id = self.env.ref('stock.route_warehouse0_mto').id
        sale_order_ids = None
        sale_qty = 0
        if from_date and to_date:
            sale_order_ids = self.env["sale.order"].search(
                [("confirmation_date", ">=", from_date), ("confirmation_date", "<=", to_date)])
        for product_id in product_ids:
            res = dict(
                (fn, 0.0) for fn in
                ['serial_no', 'product_name', 'qoh', 'make_to_order', 'lstprice', 'std_price', 'profit',
                 'forcasted_profit',
                 'sale_qty', 'image'])
            serial_no = serial_no +1
            if from_date and to_date:
                sale_qty = sum(self.env["sale.order.line"].search(
                    [("product_id", "=", product_id.id), ("order_id", "in", sale_order_ids.ids)]).mapped(
                    "qty_delivered"))
            qoh = product_id.qty_available
            profit = product_id.lst_price - product_id.standard_price
            forcasted_profit = qoh * profit
            if mto_id in product_id.route_ids.ids:
                make_to_order = "YES"
            else:
                make_to_order = "NO"
            # if product_id.categ_ids:
            #     category_list = [category_id.display_name for category_id in product_id.categ_ids]
            # else:
            #     category_list = [""]
            # for category in category_list:
            res['serial_no'] = serial_no
            res['product_name'] = product_id.name
            res['qoh']  = qoh
            res['make_to_order'] = make_to_order
            res['lstprice'] = product_id.lst_price
            res['std_price'] = product_id.standard_price
            res['profit'] = profit
            res['forcasted_profit'] = forcasted_profit
            res['sale_qty'] = sale_qty
            res['image'] = product_id.image_small
            results.append(res)

        return {
            'data': results,
            'date':to_date
        }
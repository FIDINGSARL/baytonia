from odoo import api, models

from datetime import date, timedelta, datetime

class MtoReport(models.AbstractModel):
    _name = 'report.odx_send_reports.mto_product_template'


    @api.multi
    def get_report_values(self, docids, data=None):
        from_date = str(date.today() - timedelta(days=7))
        to_date = str(date.today())


        results = []
        serial_no = 0
        mto_id = self.env.ref('stock.route_warehouse0_mto')
        product_ids = self.env["product.product"].search([("route_ids", "in", [mto_id.id])])
        for product_id in product_ids:
            serial_no =serial_no +1
            if product_id.categ_ids:
                category_list = [category_id.display_name for category_id in product_id.categ_ids]
            else:
                category_list = [""]
            for category in category_list:
                res = dict(
                    (fn, 0.0) for fn in
                    ['serial_no', 'product_name', 'qoh', 'category', 'image'])
                res['serial_no'] = serial_no
                res['product_name'] = product_id.name
                res['qoh'] = product_id.qty_available
                res['category'] = category
                res['image'] = product_id.image_small
                results.append(res)

        return {
            'data': results,
            'date':to_date
        }
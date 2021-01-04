from odoo import api, models

from datetime import date, timedelta, datetime

class MtoReport(models.AbstractModel):
    _name = 'report.odx_send_reports.non_moving_product_template'


    @api.multi
    def get_report_values(self, docids, data=None):
        from_date = str(date.today() - timedelta(days=7))
        to_date = str(date.today())

        record = self.env['stock.warehouse'].search([])

        wizard = self.env['non.moving.product.wizard.ept'].create({
            'warehouse_ids': [(6, 0, record.ids)],
            'from_date': date.today() - timedelta(days=1),
            'to_date': date.today()})
        from_date = wizard.from_date
        to_date = wizard.to_date

        today = datetime.now().strftime("%Y-%m-%d")

        warehouse_ids = wizard.warehouse_ids.ids

        data_dict = wizard.prepare_data(today, warehouse_ids, from_date, to_date)
        serial_no = 0
        for warehouse_id, data_details in data_dict.items():
            for product_data in data_details:
                serial_no = serial_no + 1
                product_id = self.env["product.product"].search([("id", "=", product_data.get("product_id"))], limit=1)
                product_data['image'] = product_id.image_small
                product_data['serial_no'] =serial_no



        return {
            'data_dict': data_dict,
            'date':to_date,
            'date_from':from_date,
            'warehouse_ids':warehouse_ids
        }
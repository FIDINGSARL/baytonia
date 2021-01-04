from datetime import date
from odoo import models, api, fields
from datetime import date, timedelta, datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT



class StockPicking(models.Model):
    _inherit = 'stock.picking'


    def delivery_status_update(self):

        from_date = str(date.today() - timedelta(days=28))
        to_date = str(date.today())
        date_to = str(to_date) + ' ' + '23:59:59'
        date_from = str(from_date) + ' ' + '00:00:00'
        domain = [('scheduled_date', '<=', date_to), ('scheduled_date', '>=', date_from)]
        delivery_order = self.search(domain)
        for delivery in delivery_order:
            if delivery.delivery_tracking_lines_ids:
                for tracking_line in delivery.delivery_tracking_lines_ids:
                    tracking_line.check_delivery_status()

    shipping_charge = fields.Float('Shipping charge', compute='_compute_shipping_charge')

    @api.depends('sale_id', 'delivery_tracking_lines_ids.carrier_id')
    def _compute_shipping_charge(self):
        for rec in self:
            if rec.sale_id and rec.delivery_tracking_lines_ids:
                for tracking_line in rec.delivery_tracking_lines_ids:
                    if tracking_line.carrier_id:
                        if tracking_line.carrier_id.delivery_type == 'Aramex':
                            order = rec.sale_id
                            shipping_dict = tracking_line.carrier_id.Aramex_rate_shipment(order)
                            if shipping_dict:
                                rec.shipping_charge = shipping_dict['price']




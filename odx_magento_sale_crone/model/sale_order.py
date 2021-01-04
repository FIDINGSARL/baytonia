from odoo import models, fields, api
from datetime import date, timedelta, datetime


class SaleOrder(models.Model):
    _inherit = 'sale.order'


    def update_magento_status_crone(self):
        from_date = str(date.today() - timedelta(days=7))
        to_date = str(date.today())
        date_to = str(to_date) + ' ' + '23:59:59'
        date_from = str(from_date) + ' ' + '00:00:00'

        sale_orders = self.search(
            [('date_order', '<=', date_to), ('date_order', '>=', date_from)])
        for sale in sale_orders:
            if sale.eg_magento_payment_method_id:
                sale.picking_ids.write({'eg_magento_payment_method_id': sale.eg_magento_payment_method_id.id})
            if sale.state:
                connectionObj = self.env['magento.configure'].search([('active', '=', True)])
                if connectionObj.auto_order_status_update:
                    status = sale.state
                    if sale.picking_ids.filtered(lambda p: p.is_complete_shipment == True):
                        status = 'shipment'
                    sale.update_magento_order_status(status)


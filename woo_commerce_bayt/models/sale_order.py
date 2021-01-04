import requests
from odoo import models, api, fields


class WooOrderStatus:
    COMPLETED = 'completed'
    DELIVERED = 'delivered'


class SaleOrder(models.Model):
    _inherit = "sale.order"

    picking_done = fields.Boolean('All Pickings Done?')
                                  # , compute='_get_picking_done', store=True)
    imported_woo_order_status = fields.Char(string="Woo Order Status at import time (not updated)")
    woo_delivered_status_updated = fields.Boolean(string="Delivered Status Updated", default=False,
                                                  help="If checked true, delivered status is updated in woo.")
    woo_completed_status_updated = fields.Boolean(string="Delivered Status Updated")
                                                  # compute="get_completed_status_updated",
                                                  # help="If checked true, completed status is updated in woo.",store=True)

    @api.multi
    def get_completed_status_updated(self):
        for order in self:
            if order.updated_in_woo:
                order.woo_completed_status_updated = True
            else:
                order.woo_completed_status_updated = False


    @api.model
    def get_woo_order_vals(self, result, workflow, invoice_address, instance, partner, shipping_address, pricelist_id,
                           fiscal_position, payment_term, payment_gateway):
        ordervals = super(SaleOrder, self).get_woo_order_vals(result, workflow, invoice_address, instance, partner,
                                                              shipping_address, pricelist_id, fiscal_position,
                                                              payment_term,
                                                              payment_gateway)
        ordervals.update({
            'imported_woo_order_status': result.get('status', False),
        })
        return ordervals


    @api.depends('picking_ids.state')
    def _get_picking_done(self):
        for order in self:
            all_pickings_states = order.picking_ids.filtered(
                lambda p: p.state != 'cancel' and p.picking_type_code == 'outgoing').mapped('state')
            if all_pickings_states and (all_pickings_states == len(all_pickings_states) * ['done']):
                order.picking_done = True
            else:
                order.picking_done = False


    @api.multi
    def auto_update_status_cron_bayt(self, ctx={}):
        woo_instance_obj = self.env['woo.instance.ept']
        instances = woo_instance_obj.search([('state', '=', 'confirmed')])
        for instance in instances:
            completed_sale_orders = self.search([('woo_instance_id', '=', instance.id), ('picking_done', '=', True),
                                                 ('woo_completed_status_updated', '!=', True)])
            completed_sale_orders.complete_order_in_woo()

            delivered_sale_orders = self.search([('woo_instance_id', '=', instance.id), ('invoice_status', '=', 'invoiced'),
                                                 ('woo_delivered_status_updated', '!=', True)])
            delivered_sale_orders.deliver_order_in_woo()
            delivered_sale_orders.write({'woo_delivered_status_updated': True})

        return True


    @api.multi
    def deliver_order_in_woo(self):
        for record in self:
            record.woo_update_order_status(WooOrderStatus.DELIVERED)
        return True


    @api.multi
    def complete_order_in_woo(self):
        for record in self:
            record.woo_update_order_status(WooOrderStatus.COMPLETED)
        return True


    @api.multi
    def woo_update_order_status(self, status):
        transaction_log_obj = self.env["woo.transaction.log"]
        for sale_order in self:
            if not sale_order.woo_instance_id or not sale_order.woo_order_id:
                continue
            instance = sale_order.woo_instance_id
            wcapi = instance.connect_in_woo()
            info = {"status": status}
            data = info
            if instance.woo_version == 'old':
                data = {"order": info}
                response = wcapi.put('orders/%s' % sale_order.woo_order_id, data)
            else:
                data.update({"id": sale_order.woo_order_id})
                response = wcapi.post('orders/batch', {'update': [data]})
            if not isinstance(response, requests.models.Response):
                message = "Update Orders %s Status \nResponse is not in proper format :: %s" % (
                    sale_order.name, response)
                log = transaction_log_obj.search(
                    [('woo_instance_id', '=', instance.id), ('message', '=', message)])
                if not log:
                    transaction_log_obj.create({'message': message,
                                                'mismatch_details': True,
                                                'type': 'sales',
                                                'woo_instance_id': instance.id
                                                })
                    continue
            if response.status_code not in [200, 201]:
                message = "Error in update order %s status,  %s" % (sale_order.name, response.content)
                log = transaction_log_obj.search(
                    [('woo_instance_id', '=', instance.id), ('message', '=', message)])
                if not log:
                    transaction_log_obj.create(
                        {'message': message,
                         'mismatch_details': True,
                         'type': 'sales',
                         'woo_instance_id': instance.id
                         })
                    continue
            try:
                result = response.json()
            except Exception as e:
                transaction_log_obj.create({
                    'message': "Json Error : While update Orders status for order no. %s to WooCommerce for "
                               "instance %s. \n%s" % (
                                   sale_order.woo_order_id, instance.name, e),
                    'mismatch_details': True,
                    'type': 'sales',
                    'woo_instance_id': instance.id
                })
                continue
            if instance.woo_version == 'old':
                errors = result.get('errors', '')
                if errors:
                    message = errors[0].get('message')
                    transaction_log_obj.create(
                        {'message': "Error in update order status,  %s" % message,
                         'mismatch_details': True,
                         'type': 'sales',
                         'woo_instance_id': instance.id
                         })
                    continue
                else:
                    sale_order.picking_ids.write({'updated_in_woo': True})
            elif instance.woo_version == 'new':
                sale_order.picking_ids.write({'updated_in_woo': True})
        return True

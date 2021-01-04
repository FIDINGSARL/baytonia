import requests

from odoo import models, api, fields


class SaleOrder(models.Model):
    _inherit = "sale.order"

    is_tracking_updated = fields.Boolean(string="Is Tracking updated?")

    @api.multi
    def auto_update_tracking_cron(self):
        woo_instance_obj = self.env['woo.instance.ept']
        instances = woo_instance_obj.search([('state', '=', 'confirmed')])
        for instance in instances:
            completed_sale_orders = self.search([('woo_instance_id', '=', instance.id), ('picking_done', '=', True),
                                                 ('is_tracking_updated', '!=', True)])
            completed_sale_orders.filtered(lambda s: s.carrier_details).update_tracking_in_woo()

    @api.multi
    def update_tracking_action(self):
        for order in self:
            if order.woo_instance_id.state == 'confirmed' and order.picking_done \
                    and not order.is_tracking_updated and order.carrier_details:
                order.update_tracking_in_woo()

    @api.multi
    def update_tracking_in_woo(self):
        for record in self:
            record.woo_update_shipment_tracking()
        return True

    @api.multi
    def woo_update_shipment_tracking(self):
        transaction_log_obj = self.env["woo.transaction.log"]
        for sale_order in self:
            if not sale_order.woo_instance_id or not sale_order.woo_order_id:
                continue
            instance = sale_order.woo_instance_id
            wcapi = instance.connect_in_woo()
            if sale_order.carrier_details:
                info = {
                    "custom_tracking_provider": "Custom",
                    "custom_tracking_link": sale_order.carrier_details,
                    "tracking_number": sale_order.picking_ids[0].carrier_tracking_ref
                }
            else:
                return
            response = wcapi.post('orders/%s/shipment-trackings' % sale_order.woo_order_id, info)

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
                message = "Error in update Tracking for order %s status,  %s" % (sale_order.name, response.content)
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
                    'message': "Json Error : While updatig tracking details for order no. %s to WooCommerce for "
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
                    sale_order.write({'is_tracking_updated': True})
            elif instance.woo_version == 'new':
                sale_order.write({'is_tracking_updated': True})
            if sale_order.is_tracking_updated:
                template = self.env.ref('export_tracking_to_woocommerce.mail_template_update_customer_order_tracking')
                sale_order.message_post_with_template(template.id)
                self._cr.commit()
        return True

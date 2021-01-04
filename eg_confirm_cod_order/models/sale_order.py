import logging

from odoo import models, api, fields

_logger = logging.getLogger("===Confirm Order Log===")


class SaleOrder(models.Model):
    _inherit = "sale.order"

    sms_attempt = fields.Integer("SMS attempt")

    @api.model
    def create(self, vals):
        order_id = super(SaleOrder, self).create(vals)
        instance_id = self.env["sms.instance"].search([("provider", "=", "unifonic_sms")])

        if instance_id:
            message = ""
            if order_id.eg_magento_payment_method_id.code in ['cod', 'COD']:
                _logger.info("Message Send for Order")
                url = "https://oddo.baytonia.com/sale_order/confirm/{}".format(order_id.id)
                message = instance_id.cod_order_msg
                message = message.replace("{{order_number}}", order_id.name)
                message = message.replace("{{url}}", url)
                # message = "Please confirm your COD order {} by clicking this URL so we can start proccesing your order. https://oddo.baytonia.com/sale_order/confirm/{}".format(
                #     order_id.name, order_id.id)
            if order_id.eg_magento_payment_method_id.code == "BANK":
                message = instance_id.bank_msg
                message = message.replace("{{order_number}}", order_id.name)
                message = message.replace("{{magento_order_amount}}", str(order_id.magento_order_amount))
            if message:
                to_number = order_id.partner_id.phone
                if not to_number and order_id.partner_id.mobile:
                    to_number = order_id.partner_id.mobile
                elif not to_number and order_id.partner_invoice_id.phone:
                    to_number = order_id.partner_invoice_id.phone
                elif not to_number and order_id.partner_invoice_id.mobile:
                    to_number = order_id.partner_invoice_id.mobile
                if to_number:
                    try:
                        self.env["post.sms.wizard"].send_sms(body=message, dst_number=to_number)
                        order_id.sms_attempt += 1
                    except Exception as e:
                        _logger.info(e)
        return order_id

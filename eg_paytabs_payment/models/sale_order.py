import json
import logging

from requests import request

from odoo import models, fields, api
from odoo.exceptions import Warning

_logger = logging.getLogger("=== PayTabs Payment ===")


class SaleOrder(models.Model):
    _inherit = "sale.order"

    payment_url = fields.Char(string="Payment URL")
    payment_id = fields.Integer(string="Payment ID")
    message = fields.Char(string="Message")
    verify_message = fields.Text(string="Verify Payment")
    paytabs_configuration_id = fields.Many2one(comodel_name="paytabs.configuration", string="Instance")

    @api.multi
    def post_data_paytabs(self, discount=None, body=None, button=None, instance=None):
        if instance:
            configuration_id = instance
            url = "https://www.paytabs.com/apiv2/create_pay_page"
            partner_id = self.partner_id
            to_number = partner_id.phone
            if not to_number and partner_id.mobile:
                to_number = partner_id.mobile
            elif not to_number and self.partner_invoice_id.phone:
                to_number = self.partner_invoice_id.phone
            elif not to_number and self.partner_invoice_id.mobile:
                to_number = self.partner_invoice_id.mobile
            if not to_number:
                raise Warning("Please add number of customer")
            # billing_id = self.partner_id
            # if not billing_id.city or not billing_id.state_id or not billing_id.zip or not billing_id.email:
            #     raise Warning("Enter complete address of Customer (City or state or zip or email)")
            # shipping_id = self.partner_id
            # if not shipping_id.city or not shipping_id.state_id or not shipping_id.zip:
            #     raise Warning("Enter complete address of Shipping")

            # product_name_list = self.order_line.mapped("product_id.name")
            # product_qty_list = self.order_line.mapped("product_uom_qty")
            # new_qty_list = []
            # for product_qty in product_qty_list:
            #     new_qty_list.append(str(product_qty))
            # product_price_list = self.order_line.mapped("price_unit")
            # new_price_list = []
            # for product_price in product_price_list:
            #     new_price_list.append(str(product_price))
            # p_name = " ||  ".join(product_name_list)
            # p_price = " ||  ".join(new_qty_list)
            # p_qty = " ||  ".join(new_price_list)
            name_billing = partner_id.name.split(" ")
            len_name_billing = len(name_billing)
            name_shipping = partner_id.name.split(" ")

            create_pay_page = {"merchant_email": configuration_id.email,
                               "secret_key": configuration_id.secret_key,
                               "site_url": configuration_id.site_url,
                               "return_url": configuration_id.return_url,
                               "title": partner_id.name,
                               "cc_first_name": name_billing[0],
                               "cc_last_name": len_name_billing == 2 and name_billing[1] or name_billing[0],
                               "cc_phone_number": "00966",
                               "phone_number": to_number,
                               "email": partner_id.email or "",
                               "products_per_title": self.name,
                               "unit_price": "{}".format(self.amount_untaxed),
                               "quantity": "1",
                               "other_charges": "{}".format(self.amount_tax),
                               "amount": "{}".format(self.amount_total),
                               "discount": discount or "",
                               "currency": partner_id.currency_id.name or "",
                               "reference_no": "ABC-123",
                               "ip_customer": "1.1.1.0",
                               "ip_merchant": "1.1.1.0",
                               "billing_address": partner_id.street,
                               "city": partner_id.city or "Jeddah",
                               "state": partner_id.state_id.code or "JED",
                               "postal_code": partner_id.zip or "21589",
                               "country": "SAU",
                               "shipping_first_name": name_shipping[0],
                               "shipping_last_name": name_shipping[1],
                               "address_shipping": partner_id.street,
                               "state_shipping": partner_id.state_id.code or "JED",
                               "city_shipping": partner_id.city or "Jeddah",
                               "postal_code_shipping": partner_id.zip or "21589",
                               "country_shipping": "SAU",
                               "msg_lang": "English",
                               "cms_with_version": "WordPress4.0-WooCommerce2.3.9"}

            try:
                response = request("POST", url, data=create_pay_page)
            except Exception as e:
                raise Warning("{}".format(e))
            if response.status_code == 200:
                response = json.loads(response.text)
                if response.get("response_code") == "4012":
                    payment_url = response.get("payment_url")
                    self.write({"payment_url": payment_url,
                                "payment_id": response.get("p_id"),
                                "paytabs_configuration_id": configuration_id.id})

                    payment_url = "Your payment url is : {}".format(payment_url)
                    body = body.replace("{{paytabs_url}}", payment_url)
                    self.message_post(body=body)
                    if self._context.get('copy'):
                        raise Warning(body)
                    if self._context.get('whatsapp'):
                        url = 'https://web.whatsapp.com/send?phone='
                        if to_number:
                            dst_number = to_number
                            dst_number = dst_number.lstrip("0")
                            dst_number = dst_number.lstrip("+")
                            dst_number = dst_number.lstrip("966")
                            to_number = "+966{}".format(dst_number)
                        url += to_number + "&text=" + body
                        return {'type': 'ir.actions.act_url',
                                'name': "Send Sale Order",
                                'target': 'new',
                                'url': url}
                    self.env["post.sms.wizard"].send_sms(self, body=body, dst_number=to_number)
                else:
                    if button:
                        error = None
                        if response.get("details"):
                            error = response.get("details")
                        elif response.get("result"):
                            error = response.get("result")
                        _logger.info("error is : {}".format(error))
                        self._cr.commit()
                        raise Warning("error is : {}".format(error))
            else:
                if button:
                    _logger.info("Connection is not success")
                    self._cr.commit()
                    raise Warning("Connection is not success")

        else:
            if button:
                _logger.info("Please do or Select Paytab configuration first!!!")
                self._cr.commit()
                raise Warning("Please do or Select Paytab configuration first!!!")

    @api.multi
    def paytabs_verify_payment(self):
        order_ids = self.browse(self._context.get("active_ids"))
        if order_ids:
            for order_id in order_ids:
                configuration_id = order_id.paytabs_configuration_id
                if order_id.payment_id and configuration_id:
                    url = "https://www.paytabs.com/apiv2/verify_payment"
                    verify_payment = {"merchant_email": configuration_id.email,
                                      "secret_key": configuration_id.secret_key,
                                      "payment_reference": "{}".format(order_id.payment_id)
                                      }
                    try:
                        response = request("POST", url, data=verify_payment)
                    except:
                        continue
                    if response.status_code == 200:
                        response = json.loads(response.text)
                        if response.get("response_code") == "100":
                            result = response.get("result")
                            order_id.write({"verify_message": result})
                        else:
                            error = None
                            if response.get("result"):
                                error = response.get("result")
                            elif response.get("details"):
                                error = response.get("details")
                            order_id.write({"verify_message": error})

# -*- coding: utf-8 -*-
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger("===ORDER CONFIRM===")


class ConfirmCODOrder(http.Controller):

    @http.route('/sale_order/confirm/<order_id>', type='http', auth="public")
    def confirm_sale_order(self, order_id, **kwargs):
        so_order_id = request.env['sale.order'].sudo().search([('id', '=', int(order_id))])
        if so_order_id:
            if so_order_id.state == "draft":
                _logger.info("Order Going to confirm")
                so_order_id.action_confirm()
                so_order_id.message_post("Order confirmed by {}".format(so_order_id.partner_id.name))
                message = """
                                <html>
                                    <body onload="myFunction()">
                                        <script>
                                        function myFunction() {
                                        alert("Dear %s,Thank you. Your order %s has been confirm.");
                                        window.location ="https://baytonia.com"
                                        }
                                        
                                        </script>
                                        
                                    </body>
                                </html>
                            """ % (so_order_id.partner_id.name, so_order_id.name)
                return message
                # return "<h3>Dear {},<br/>Thanks Your Order <h2>{}</h2> confirmation.</h3>".format(
                #     so_order_id.partner_id.name, so_order_id.name)
            else:
                _logger.info("Order is already confirmed")
                message = """
                                <html>
                                    <body onload="myFunction()">
                                        <script>
                                        function myFunction() {
                                        alert("Dear %s,Your order %s has been already confirmed..");
                                        window.location ="https://baytonia.com"
                                        }
                                        
                                        </script>
                                        
                                    </body>
                                </html>
                                """ % (so_order_id.partner_id.name, so_order_id.name)
                return message
                # return "<h2>Dear {},<br/>Your Order <b>{}</b> Has been already confirmed.</h2>".format(
                #     so_order_id.partner_id.name, so_order_id.name)
        else:
            message = """
                        <html>
                            <body onload="myFunction()">
                                <script>
                                function myFunction() {
                                alert("We are unable to find your order. Kindly contact our customer support at WeCare@baytonia.com.");
                                window.location ="https://baytonia.com"
                                }

                                </script>

                            </body>
                        </html>
                        """
            return message

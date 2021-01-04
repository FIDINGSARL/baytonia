# -*- coding: utf-8 -*-
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger("===Deliver Return CONFIRM===")


class ConfirmDeliveryReturn(http.Controller):

    @http.route('/delivery_return/confirm/<order_id>', type='http', auth="public")
    def confirm_delivery_return(self, order_id, **kwargs):
        picking_id = request.env['stock.picking'].sudo().search([('id', '=', int(order_id))])
        if picking_id:
            if picking_id.state == "done":
                _logger.info("Return Going to confirm")
                picking_id.return_accepted = True
                picking_id.message_post("Return confirmed by {}".format(picking_id.partner_id.name))
                message = """
                                <html>
                                    <body onload="myFunction()">
                                        <script>
                                        function myFunction() {
                                        alert("Dear %s,Thank you. Your return %s has been confirm.");
                                        window.location ="https://baytonia.com"
                                        }
                                        
                                        </script>
                                        
                                    </body>
                                </html>
                            """ % (picking_id.partner_id.name, picking_id.name)
                return message
            else:
                _logger.info("Return is already confirmed")
                message = """
                                <html>
                                    <body onload="myFunction()">
                                        <script>
                                        function myFunction() {
                                        alert("Dear %s,Your return %s has been already confirmed..");
                                        window.location ="https://baytonia.com"
                                        }
                                        
                                        </script>
                                        
                                    </body>
                                </html>
                                """ % (picking_id.partner_id.name, picking_id.name)
                return message

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

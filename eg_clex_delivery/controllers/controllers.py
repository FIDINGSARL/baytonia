# -*- coding: utf-8 -*-
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger("===ORDER CONFIRM===")


class GetTrackingCLEX(http.Controller):

    @http.route('/shipment/track/clex', type='http', methods=['GET', 'POST'], auth="public")
    def fetch_clex_status(self, **kwargs):
        _logger.info(["clex_log", kwargs])
        so_order_id = request.env['sale.order'].sudo().search([('id', '=', 1000)])
        if kwargs:
            so_order_id.message_post(body="{}".format(kwargs))

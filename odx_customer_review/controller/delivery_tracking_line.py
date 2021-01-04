# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import logging
import werkzeug
from datetime import datetime
from math import ceil
import requests
import json
from odoo import fields, http, SUPERUSER_ID
from odoo.http import request
from odoo.tools import ustr
from odoo.http import request, Response

_logger = logging.getLogger(__name__)


class UpdateDeliveryStatus(http.Controller):
    @http.route(['/delivery/update/status'],type='json',csrf=False, auth='none',methods=['POST'])
    def update_delivery_status(self, **post):
        data = json.loads(request.httprequest.data)
        shipmentId = data.get('shipmentId')
        _logger.info("Delivery Status")
        _logger.info(shipmentId,"shipmentId")
        delivery_tracking_lines = request.env['delivery.tracking.line'].sudo().search([('tracking_ref', 'ilike', shipmentId)])
        for delivery in delivery_tracking_lines:
            delivery.sudo().check_delivery_status()
            if delivery.picking_id:
                if delivery.picking_id.sale_id:
                    delivery.picking_id.sale_id.sudo().check_delivery_status_bulk_fl()


        return data



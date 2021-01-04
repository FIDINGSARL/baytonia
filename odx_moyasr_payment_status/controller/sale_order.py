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

_logger = logging.getLogger(__name__)


class SaleOrderMoyasar(http.Controller):
    # HELPER METHODS #

    @http.route(['/sale/confirm/payment'], type='json',csrf=False, auth='public', website=True,methods=['POST'])
    def confirm_order_moyasar(self, **post):
        _logger.info("Moyasar payment")
        sale_order = request.env['sale.order'].sudo().moyasar_payment_status()




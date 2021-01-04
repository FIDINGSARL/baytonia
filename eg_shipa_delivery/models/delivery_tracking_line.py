import logging

import requests

from odoo import api, models
from odoo.exceptions import Warning

_logger = logging.getLogger(__name__)


class DeliveryStatusUPS(models.Model):
    _inherit = "delivery.tracking.line"

    @api.multi
    def shipa_delivery_check_delivery_status(self):
        self.ensure_one()
        try:
            headers = {
                'Accept': 'application/json',
            }
            params = (
                ('apikey', self.carrier_id.shipa_api_key),
            )
            url = 'https://api.shipadelivery.com/orders/{}/history'.format(self.tracking_ref)
            response = requests.get(url, headers=headers, params=params).json()
            _logger.info("=====SHIPA PAYMENT REG RES=== {}".format(response))
            if response.get("info") == "Success":
                if isinstance(response.get('history'), list) and len(response.get('history')) > 0:
                    return response.get('history')[-1].get('code')
        except Exception as e:
            raise Warning(e)

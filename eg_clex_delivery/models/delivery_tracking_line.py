import json
import logging

import requests

from odoo import api, models
from odoo.exceptions import Warning

_logger = logging.getLogger(__name__)


class DeliveryStatusUPS(models.Model):
    _inherit = "delivery.tracking.line"

    @api.multi
    def clex_delivery_check_delivery_status(self):
        self.ensure_one()
        try:
            url = "https://api.clexsa.com/consignment/track-status"
            headers = {"Content-Type": "application/json",
                       "Access-token": self.carrier_id.clex_access_token}
            body = {"shipment_id": self.tracking_ref}
            payload = json.dumps(body)
            response = requests.request("POST", url, data=payload, headers=headers)

            if response.status_code == 200:
                response_dict = json.loads(response.text)
                _logger.info("=====CLEX RESPONSE=== {}".format(response_dict))
                if response_dict.get("message") == "Success":
                    data = response_dict.get("data")
                    _logger.info(data)
                    if data and data.get(self.tracking_ref) and data.get(self.tracking_ref).get(
                            'detail'):
                        _logger.info(data.get(self.tracking_ref).get('detail'))
                        return data.get(self.tracking_ref).get('detail')
        except Exception as e:
            raise Warning(e)

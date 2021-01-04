import logging

import requests

from odoo import api, models
from odoo.exceptions import Warning

_logger = logging.getLogger(__name__)


class DeliveryStatusUPS(models.Model):
    _inherit = "delivery.tracking.line"

    @api.multi
    def vaal_check_delivery_status(self):
        self.ensure_one()
        try:
            headers = self.carrier_id.get_vaal_headers()
            url = "https://deliver.vaal.me/ords/vaal/api/v2/orders/status/%s" % (self.tracking_ref)
            res = requests.get(url, headers=headers).json()
            _logger.info("=====VAAL PAYMENT REG RES=== {}".format(res))
            if res.get('status_en'):
                return res.get('status_en')
        except Exception as e:
            raise Warning(e)

import logging

import requests

from odoo import api, models
from odoo.exceptions import Warning

_logger = logging.getLogger(__name__)


class DeliveryStatusUPS(models.Model):
    _inherit = "delivery.tracking.line"

    @api.multi
    def saee_check_delivery_status(self):
        self.ensure_one()
        try:
            track_url = "http://www.saee.sa/tracking?trackingnum="
            res = requests.get("%s%s" % (track_url, self.tracking_ref)).json()
            _logger.info("=====SAEE PAYMENT REG RES=== {}".format(res))
            if res.get('details'):
                return res.get('details')[0].get('notes')
        except Exception as e:
            raise Warning(e)

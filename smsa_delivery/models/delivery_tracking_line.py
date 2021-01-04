import logging

from odoo import api, models
from odoo.exceptions import Warning

_logger = logging.getLogger(__name__)


class DeliveryStatusUPS(models.Model):
    _inherit = "delivery.tracking.line"

    @api.multi
    def smsa_check_delivery_status(self):
        self.ensure_one()
        try:
            client = self.carrier_id.get_smsa_client()
            if self.tracking_ref:
                res = client.service.getStatus(passkey=self.carrier_id.smsa_pass_key,
                                               awbNo=self.tracking_ref)
                _logger.info("=====SMSA PAYMENT REG RES=== {}".format(res))
                return res
        except Exception as e:
            raise Warning(e)

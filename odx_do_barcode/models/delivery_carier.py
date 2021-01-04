import logging

from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    eg_magento_payment_method_id = fields.Many2many(comodel_name="magento.payment.method",
                                                    string="Allowed M Payment Method")

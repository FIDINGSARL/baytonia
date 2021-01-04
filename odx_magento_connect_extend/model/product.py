import base64
import json
import logging

import requests

from odoo import models, api, fields
from odoo.http import request

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = "product.template"

    compare_magento_varients = fields.Boolean('No Of Variants In Magento', compute='_compute_compare_magento_varients')

    @api.depends('product_variant_count', 'product_variant_ids')
    def _compute_compare_magento_varients(self):
        for rec in self:
            no_of_magento_varients = 0
            for varient in rec.product_variant_ids:
                ctx = dict(self._context)
                magento_configure_id = self.env["magento.configure"].search(
                    [("active", "=", True), ("state", "=", "enable")])
                if magento_configure_id:
                    ctx.update({"instance_id": magento_configure_id.id})
                    connection = self.env["magento.configure"].with_context(ctx)._create_connection()
                    if connection:
                        url = connection[0]
                        token = connection[1]
                        api_url = "{}/rest/V1/products/{}".format(url, varient.default_code)
                        userAgent = request.httprequest.environ.get('HTTP_USER_AGENT', '')
                        headers = {'Authorization': token,
                                   'Content-Type': 'application/json', 'User-Agent': userAgent}

                        response = requests.request("GET", url=api_url, headers=headers, params='')
                        if response:
                            no_of_magento_varients += 1
            if rec.product_variant_count == no_of_magento_varients:
                rec.compare_magento_varients = True
            else:
                rec.compare_magento_varients = False



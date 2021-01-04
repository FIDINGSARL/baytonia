import base64
import json
import logging

import requests
from odoo.http import request

from odoo import models, api, fields
from odoo.exceptions import Warning

_logger = logging.getLogger("====Product_Product====")


class ProductProduct(models.Model):
    _inherit = "product.product"

    magento_product_type = fields.Selection(
        [('simple', 'Simple Product'), ('virtual', 'Virtual Product'), ('configurable', 'Configurable Product'),
         ('downloadable', 'Downloadable Product '), ('grouped', 'Grouped Product'), ('bundle', 'Bundle Product '),
         ('amgiftcard', 'Gift Card Product')], string='Magento Product Type')
    is_extra_fee = fields.Boolean('Is Extra fee')

    def update_magento_product_type(self):
        ctx = dict(self._context)
        magento_configure_id = self.env["magento.configure"].search(
            [("active", "=", True), ("state", "=", "enable")])
        if magento_configure_id:
            ctx.update({"instance_id": magento_configure_id.id})
            connection = self.env["magento.configure"].with_context(ctx)._create_connection()
            if connection:
                url = connection[0]
                token = connection[1]
                api_url = "{}/rest/V1/products/{}".format(url, self.default_code)
                # userAgent = request.httprequest.environ.get('HTTP_USER_AGENT', '')
                headers = {'Authorization': token,
                           'Content-Type': 'application/json'}
                try:
                    userAgent = request.httprequest.environ.get('HTTP_USER_AGENT', '')
                    headers.update({'User-Agent': userAgent})
                except Exception as e:
                    pass

                response = requests.request("GET", url=api_url, headers=headers, params='')
                if response:
                    data = response.json()
                    if data:
                        self.magento_product_type = data.get('type_id')

    def update_magento_product_type_crone(self):
        products = self.search([('magento_product_type', '=', False)], limit=50)
        for product in products:
            product.update_magento_product_type()

    def update_odoo_to_magento_price_qty_name(self):
        ctx = dict(self._context)
        magento_configure_id = self.env["magento.configure"].search([("active", "=", True), ("state", "=", "enable")])
        text = ""
        status = "no"
        product_id = self
        magento_product_id = self.env["magento.product"].search([("pro_name", "=", product_id.id)])
        if magento_product_id:
            qty_available = product_id.with_context(location=magento_configure_id.location_id.id).qty_available

            update = self._context.get("update")
            if not update:
                if not product_id.sale_ok:
                    return True
                # if qty_available == magento_product_id.product_quantity:
                #     return True

            if magento_configure_id:
                ctx.update({"instance_id": magento_configure_id.id})
                connection = self.env["magento.configure"].with_context(ctx)._create_connection()
                if connection:
                    url = connection[0]
                    token = connection[1]
                    stock_item_id = magento_product_id.magento_stock_id
                    api_url = "{}/rest/V1/custom/product-update".format(url)
                    #
                    data = {
                        "sku": product_id.default_code,
                        "price": product_id.lst_price,
                        "name": product_id.name,
                        "qty": qty_available
                    }

                    headers = {'Accept': '*/*', 'Content-Type': 'application/json',
                               'Authorization': token}
                    try:

                        response = requests.request("PUT", url=api_url, headers=headers, data=json.dumps(data))
                    except Exception as e:
                        text = "{}".format(e)
                        response = None
                    if response:
                        if response.status_code == 200:
                            response = json.loads(response.text)
                            if response == str(stock_item_id):
                                magento_product_id.write({"product_quantity": qty_available})
                                text = "Success to update product quantity and backorder: {}".format(
                                    product_id.display_name)
                                status = "yes"
                            else:
                                text = "Connection is success but this product: {} is not update".format(
                                    product_id.display_name)
                        else:
                            text = "Magento error: {} for update quantity and backorder this product: {}".format(
                                response.text,
                                product_id.display_name)

            else:
                text = "Magento product update quantity and backorder error for : {} , Could not able to connect magento".format(
                    product_id.display_name)
        else:
            text = "This product is not mapping: {}".format(product_id.name)
        self.env['magento.sync.history'].create(
            {'status': status, 'action_on': 'product', 'action': 'c', 'error_message': text})
        self._cr.commit()

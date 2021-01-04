import base64
import json
import logging

import requests

from odoo import models, api, fields
from odoo.exceptions import Warning

_logger = logging.getLogger("====Product_Product====")


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def create(self, vals):
        _logger.info(["Create", vals])
        res = super(ProductProduct, self).create(vals)
        ctx = dict(self._context or {})
        if 'magento' in ctx:
            res.type = "product"
        return res

    back_order = fields.Boolean(string="Back Order")
    magento_publish = fields.Boolean(string="Magento Publish")
    threshold_qty = fields.Float('Out-of-Stock Threshold')

    @api.multi
    def write(self, vals):
        _logger.info(["Write", vals])
        res = super(ProductProduct, self).write(vals)
        ctx = dict(self._context or {})
        if 'magento' in ctx:
            for rec in self:
                if rec.type != 'product':
                    rec.write({'type': 'product'})
        return res

    # @api.multi
    # def write(self, vals):
    #     mto_id = self.env.ref('stock.route_warehouse0_mto').id
    #     already_mtp = False
    #     if vals.get('route_ids'):
    #         if mto_id in self.route_ids.ids:
    #             already_mtp = True
    #     res = super(ProductProduct, self).write(vals)
    #     if vals.get('route_ids'):
    #         mto_id = self.env.ref('stock.route_warehouse0_mto').id
    #         if already_mtp and mto_id not in self.route_ids.ids:
    #             self.update_back_order_magento("unchecked")
    #         elif not already_mtp and mto_id in self.route_ids.ids:
    #             self.update_back_order_magento("checked")
    #     return res
    #
    # @api.multi
    # def update_back_order_magento(self, make_to_order):
    #     ctx = dict(self._context or {})
    #     connectionObj = self.env['magento.configure'].search([('active', '=', True)])
    #     ctx['instance_id'] = connectionObj.id
    #     text = ""
    #     if connectionObj.active:
    #         if connectionObj.state != 'enable':
    #             return False
    #     else:
    #         text = 'Magento BACK ORDER Error For  %s >> Could not able to connect Magento.' % (self.name)
    #     for rec in self:
    #         connection = self.env['magento.configure'].with_context(ctx)._create_connection()
    #         status = ""
    #
    #         if connection:
    #             url = connection[0]
    #             token = connection[1]
    #             path = '/V1//updatebackorder/{}'.format(rec.default_code or rec.barcode)
    #             back_order = 1 if make_to_order == "checked" else 0
    #             api_url = '{}{}'.format(url, path)
    #             headers = {'Accept': '*/*',
    #                        'Content-Type': 'application/json',
    #                        'Authorization': token}
    #             if api_url:
    #                 data = {
    #                     "product": {
    #                         "backorders": back_order
    #                     }
    #                 }
    #                 api_response = requests.post(api_url, headers=headers, data=json.dumps(data), verify=False)
    #                 if api_response:
    #                     text = 'Backorder of %s || %s has been successfully updated on magento.' % (
    #                         self.name, self.default_code)
    #                     status = 'yes'
    #                 else:
    #                     text = 'Magento %s Error for Product %s || %s, Error' % (
    #                         api_response, self.name, self.default_code)
    #                     status = 'no'
    #
    #         self.env['magento.sync.history'].create(
    #             {'status': status, 'action_on': 'order', 'action': 'b', 'error_message': text})
    #         self._cr.commit()
    #     return

    @api.multi
    def get_product_media(self):
        ctx = dict(self._context)
        magento_configure_id = self.env["magento.configure"].search([("active", "=", True), ("state", "=", "enable")])
        text = ""
        status = "no"
        product_id = self
        magento_product_id = self.env["magento.product"].search([("pro_name", "=", product_id.id)])
        if not magento_product_id:
            raise Warning("This product is not mapping: {}".format(product_id.name))

        if magento_configure_id:
            ctx.update({"instance_id": magento_configure_id.id})
            connection = self.env["magento.configure"].with_context(ctx)._create_connection()
            if connection:
                url = connection[0]
                token = connection[1]
                path = "/rest/V1/products/{}/media".format(product_id.default_code)
                api_url = '{}{}'.format(url, path)
                headers = {'Accept': '*/*', 'Content-Type': 'application/json',
                           'Authorization': token}
                try:
                    response = requests.request("GET", url=api_url, headers=headers, verify=False)
                except Exception as e:
                    text = "{}".format(e)
                    response = None
                if response:
                    if response.status_code == 200:
                        response = json.loads(response.text)
                        if response:
                            file = response[0].get("file")
                            image_url = "{}/media/catalog/product{}".format(url, file)
                            response_image = requests.get(image_url)
                            if response_image.status_code == 200:
                                text = "Success to fetch image for this product: {}".format(product_id.display_name)
                                status = "yes"
                                img = base64.b64encode(response_image.content)
                                product_id.write({"image": img})
                            else:
                                text = "Connection is success but this product: {} have no image in magento".format(
                                    product_id.display_name)
                        else:
                            text = "Connection is success but this product : {} is not available in magento".format(
                                product_id.display_name)
                    else:
                        text = "Magento error: {} for get media this product: {}".format(response.text,
                                                                                         product_id.display_name)
        else:
            text = "Magento product image fetch error for : {} , Could not able to connect magento".format(
                product_id.display_name)

        self.env['magento.sync.history'].create(
            {'status': status, 'action_on': 'product', 'action': 'a', 'error_message': text})
        self._cr.commit()

    @api.multi
    def cron_for_fetch_product_image(self, limit=150):
        domain = [('pro_name.sale_ok', '=', True)]
        if limit > 150:
            product_ids = self.env["magento.product"].search(domain, limit=limit)
        else:
            product_ids = self.env["magento.product"].search(domain)
        for product_id in product_ids:
            if not product_id.pro_name.image:
                product_id.pro_name.get_product_media()

    @api.multi
    def action_update_product_qty_to_magento(self):
        for rec in self:
            if rec.sale_ok:
                rec.with_context(update=True).update_product_quantity()

    @api.multi
    def update_product_quantity(self):
        ctx = dict(self._context)
        magento_configure_id = self.env["magento.configure"].search([("active", "=", True), ("state", "=", "enable")])
        text = ""
        status = "no"
        product_id = self
        magento_product_id = self.env["magento.product"].search([("pro_name", "=", product_id.id)], limit=1)
        if magento_product_id:
            qty_available = product_id.with_context(location=magento_configure_id.location_id.id).qty_available
            threshold_qty = product_id.with_context(location=magento_configure_id.location_id.id).threshold_qty

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
                    route_id = self.env.ref('stock_mts_mto_rule.route_mto_mts')
                    stock_item_id = magento_product_id.magento_stock_id
                    api_url = "{}/rest/V1/products/{}/stockItems/{}".format(url, product_id.default_code,
                                                                            stock_item_id)
                    # qty_available = product_id.with_context(location=magento_configure_id.location_id.id).qty_available
                    # threshold_qty = product_id.with_context(location=magento_configure_id.location_id.id).threshold_qty
                    if product_id.route_ids:
                        if route_id in product_id.route_ids:
                            back_order = True
                        else:
                            back_order = False
                    else:
                        back_order = False
                    # back_order = 1 if product_id.back_order else 0
                    # if back_order and magento_configure_id.manage_back_order:
                    #     is_in_stock = True
                    if qty_available > 0:
                        is_in_stock = True
                    else:
                        is_in_stock = False
                    if back_order:
                        stock_item_dict = {
                            "itemId": stock_item_id,
                            "productId": magento_product_id.mag_product_id,
                            "stockId": 1,
                            # "use_config_min_qty": False,
                            "use_config_backorders": False,
                            # "min_qty": int(threshold_qty),
                            "qty": int(qty_available),
                            # "isInStock": is_in_stock,
                            # "backorders": back_order
                        }
                    else:
                        stock_item_dict = {
                            "itemId": stock_item_id,
                            "productId": magento_product_id.mag_product_id,
                            "stockId": 1,
                            "qty": int(qty_available),
                            "isInStock": is_in_stock,
                            # "use_config_min_qty": True,
                            # "use_config_backorders": True,
                        }
                    # if magento_configure_id.manage_back_order:
                    #     stock_item_dict.update({"backorders": back_order})
                    data = {
                        "stockItem": stock_item_dict
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

    @api.multi
    def update_product_odoo_to_magento(self):
        for rec in self:
            if rec.sale_ok:
                rec.with_context(update=True).update_product_quantity()
                rec.update_product_status()

    @api.multi
    def update_product_status(self):
        ctx = dict(self._context)
        magento_configure_id = self.env["magento.configure"].search([("active", "=", True), ("state", "=", "enable")])
        if not magento_configure_id.manage_product_status:
            return
        text = ""
        status = "no"
        product_id = self
        magento_product_id = self.env["magento.product"].search([("pro_name", "=", product_id.id)])
        if magento_product_id and magento_configure_id:
            ctx.update({"instance_id": magento_configure_id.id})
            connection = self.env["magento.configure"].with_context(ctx)._create_connection()
            if connection:
                url = connection[0]
                token = connection[1]
                api_url = "{}/rest/V1/products/{}".format(url, product_id.default_code)
                magento_publish = 1 if product_id.magento_publish else 2
                product_dict = {"product": {"sku": product_id.default_code,
                                            "status": magento_publish}}
                headers = {'Accept': '*/*', 'Content-Type': 'application/json',
                           'Authorization': token}
                try:
                    response = requests.request("PUT", url=api_url, headers=headers, data=json.dumps(product_dict))

                except Exception as e:
                    text = "{}".format(e)
                    response = None
                if response:
                    if response.status_code == 200:
                        response = json.loads(response.text)
                        if response.get("status") == magento_publish:
                            text = "Success to update product status: {}".format(
                                product_id.display_name)
                            status = "yes"
                        else:
                            text = "Connection is success but this product: {} is not update".format(
                                product_id.display_name)
                    else:
                        text = "Magento error: {} for update status this product: {}".format(
                            response.text,
                            product_id.display_name)

            else:
                text = "Magento product update status error for : {} , Could not able to connect magento".format(
                    product_id.display_name)
        else:
            text = "This product is not mapping: {}".format(product_id.name)
        self.env['magento.sync.history'].create(
            {'status': status, 'action_on': 'product', 'action': 'c', 'error_message': text})
        self._cr.commit()

    @api.multi
    def cron_for_update_product_quantity(self, limit=10):
        domain = [('pro_name.sale_ok', '=', True)]
        if limit > 10:
            product_ids = self.env["magento.product"].search(domain, limit=limit)
        else:
            product_ids = self.env["magento.product"].search(domain)
        for product_id in product_ids:
            product_id.pro_name.update_product_quantity()

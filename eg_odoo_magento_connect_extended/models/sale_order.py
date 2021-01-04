import json
import logging
from datetime import datetime, timedelta

import requests

from odoo import models, fields, api
from odoo.exceptions import Warning
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)

STATUS_MAPPING = {
    'draft': 'pending',
    'sale': 'processing',
    'done': 'complete',
    'cancel': 'canceled',
    'shipment': 'shipmentOut',
    'invoice': 'complete'
}


class SaleOrder(models.Model):
    _inherit = "sale.order"

    eg_magento_payment_method_id = fields.Many2one("magento.payment.method", "M Payment Method")
    magento_order_amount = fields.Float("Magento Order Amount")
    status_fetched = fields.Boolean("Status fetached from magento")
    eg_invoice_policy = fields.Selection([('order', 'Ordered quantities'), ('delivery', 'Delivered quantities')],
                                         string='Invoicing Policy', default="delivery")
    register_popup = fields.Boolean(related="eg_magento_payment_method_id.register_popup")
    need_update_from_magento = fields.Boolean(string="Update Magento", default=True)

    @api.model
    def create(self, vals):
        _logger.info(["=====Payment Method Name=====", vals.get("payment_method_name")])
        if vals.get("payment_method_name"):
            magento_payment_method_id = self.env["magento.payment.method"].search(
                [('name', '=', vals.get("payment_method_name"))])
            if not magento_payment_method_id:
                magento_payment_method_id = self.env["magento.payment.method"].create(
                    {'name': vals.get("payment_method_name")})
            vals.update({
                'eg_magento_payment_method_id': magento_payment_method_id.id
            })
            if magento_payment_method_id.eg_invoice_policy == "order":
                vals.update({
                    'eg_invoice_policy': magento_payment_method_id.eg_invoice_policy
                })
        res = super(SaleOrder, self).create(vals)
        if res.eg_magento_payment_method_id.product_id and res.eg_magento_payment_method_id.charges:
            res.create_sale_order_line()
        res.set_tax_on_product()
        return res

    def create_sale_order_line(self):
        sale_order_line_obj = self.env['sale.order.line']
        sale_order_line = sale_order_line_obj.new({
            'order_id': self.id,
            'product_id': self.eg_magento_payment_method_id.product_id.id,
            'name': self.eg_magento_payment_method_id.product_id.display_name,
        })
        sale_order_line.product_id_change()
        sale_order_line.price_unit = self.eg_magento_payment_method_id.charges or 0
        sale_order_line_values = sale_order_line._convert_to_write(sale_order_line._cache)
        sale_order_line_obj.create(sale_order_line_values)

    def set_tax_on_product(self):
        _logger.info(["=== Outer Set Tax on sale order===", self.partner_id.country_id.code])
        if self.partner_id.country_id and self.partner_id.country_id.code == "SA":
            _logger.info(["=== inner Set Tax on sale order===", self.partner_id.country_id.code])
            tax_id = self.env["account.tax"].search([("default_tax", "=", True)])
            _logger.info(
                ["===FOUND Tax ID===", tax_id])
            if not tax_id:
                return True
            for order_line_id in self.order_line:
                if not order_line_id.tax_id:
                    _logger.info(
                        ["=== Setting up tax===", self.partner_id.country_id.code, order_line_id.tax_id])
                    order_line_id.tax_id = [(6, 0, tax_id.ids)]

    # @api.onchange('eg_magento_payment_method_id')
    # def _onchange_eg_magento_payment_method_id(self):
    #     if self.picking_ids.filtered(lambda p: p.state == 'done'):
    #         raise ValidationError("There must not be any Done Delivery Order!!")

    @api.multi
    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        if vals.get("eg_magento_payment_method_id"):
            # if self.picking_ids.filtered(lambda p: p.state == 'done'):
            #     # raise ValidationError("There must not be any Done Delivery Order!!")
            # else:
            self.picking_ids.write({'eg_magento_payment_method_id': self.eg_magento_payment_method_id.id})
        if vals.get("state"):
            connectionObj = self.env['magento.configure'].search([('active', '=', True)])
            if connectionObj.auto_order_status_update:
                self.update_magento_order_status(vals.get("state"))
        return res

    @api.multi
    def update_magento_order_status(self, state):
        if state == "invoice":
            return
        ctx = dict(self._context or {})
        connectionObj = self.env['magento.configure'].search([('active', '=', True)])
        ctx['instance_id'] = connectionObj.id
        text = ""
        status = "no"
        for rec in self:
            if connectionObj.active:
                if connectionObj.state != 'enable':
                    return False
            else:
                text = 'Magento SO update Error For  %s >> Could not able to connect Magento.' % (rec.name)

            connection = self.env['magento.configure'].with_context(ctx)._create_connection()
            if connection:
                url = connection[0]
                token = connection[1]
                status = STATUS_MAPPING.get(state)
                order_mapping_id = self.env["wk.order.mapping"].search([('erp_order_id', '=', rec.id)])
                magento_id = order_mapping_id.ecommerce_order_id
                path = '/rest/V1/orders'.format(magento_id)
                # path = '/rest/V1/orders/{}/comments'.format(magento_id)
                api_url = '{}{}'.format(url, path)
                headers = {'Accept': '*/*', 'Content-Type': 'application/json',
                           'Authorization': token}
                if state == 'shipment':
                    data = {

                        "entity": {
                            "entity_id": magento_id,
                            "state": "complete",
                            "status": status,
                        }

                    }

                elif state == 'sale':
                    data = {

                        "entity": {
                            "entity_id": magento_id,
                            "state": "processing",
                            "status": status,
                        }

                    }
                elif state == 'cancel':
                    data = {

                        "entity": {
                            "entity_id": magento_id,
                            "state": "canceled",
                            "status": status,
                        }

                    }
                else:
                    data = {

                        "entity": {
                            "entity_id": magento_id,
                            "status": status,
                        }

                    }
                api_response = requests.post(api_url, headers=headers, data=json.dumps(data), verify=False)
                if api_response:
                    text = 'Status of Sale order %s  has been successfully updated on magento.' % (
                        rec.name)
                    status = 'yes'
                    rec.status_updated_on_magento = True
                else:
                    text = 'Magento %s Error for SO %s Error' % (api_response, rec.name)
                    status = 'no'

                self.env['magento.sync.history'].create(
                    {'status': status, 'action_on': 'order', 'action': 'b', 'error_message': text})
        self.env['magento.sync.history'].create(
            {'status': status, 'action_on': 'order', 'action': 'b', 'error_message': text})

    @api.multi
    def cron_for_fetch_order_status(self):
        time_to_check = datetime.now() - timedelta(hours=24)
        time_to_check = time_to_check.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        order_ids = self.env["sale.order"].search([('state', '=', 'draft'),
                                                   ('eg_magento_payment_method_id.auto_process', '=', True),
                                                   ('create_date', '>', time_to_check)])
        for order_id in order_ids:
            order_id.fetch_magento_order_status_from_magento()
            self._cr.commit()

    @api.multi
    def action_fetch_magento_order_status_from_magento(self):
        for rec in self:
            if rec.state == "draft" and rec.eg_magento_payment_method_id and \
                    rec.eg_magento_payment_method_id.auto_process:
                rec.fetch_magento_order_status_from_magento()
            self._cr.commit()

    @api.multi
    def fetch_magento_order_status_from_magento(self):
        ctx = dict(self._context or {})
        connectionObj = self.env['magento.configure'].search([('active', '=', True)])
        if not connectionObj.confirmation_states:
            return
        ctx['instance_id'] = connectionObj.id
        text = ""
        status = "no"
        if connectionObj.active:
            if connectionObj.state != 'enable':
                return False
        else:
            text = 'Magento SO update Error For  %s >> Could not able to connect Magento.' % (self.name)
        for rec in self:
            connection = self.env['magento.configure'].with_context(ctx)._create_connection()
            if connection:
                url = connection[0]
                token = connection[1]

                order_mapping_id = self.env["wk.order.mapping"].search([('erp_order_id', '=', rec.id)])
                magento_id = order_mapping_id.ecommerce_order_id
                path = '/rest/V1/orders/{}'.format(magento_id)
                api_url = '{}{}'.format(url, path)
                headers = {'Accept': '*/*', 'Content-Type': 'application/json',
                           'Authorization': token}
                api_response = requests.get(api_url, headers=headers)
                if api_response.status_code == 200:
                    response = json.loads(api_response.text)
                    order_state = response.get('status')
                    _logger.info(
                        "=====response = {} ====order stute {} and need to update {}=====".format(
                            response.get('status'), order_state, self.need_update_from_magento))
                    states = connectionObj.confirmation_states.split(",")
                    if self.state == "draft" and order_state in states and not self.need_update_from_magento:
                        _logger.info("Order Confirmed")
                        self.action_confirm()
                        self.message_post("Order confirmed by system based on Magento status")
                    elif self.state == "draft" and order_state in states:
                        self.get_magento_sale_order(method="verify")
                        if not self.need_update_from_magento:
                            _logger.info("Order Confirmed")
                            self.action_confirm()
                            self.message_post("Order confirmed by system based on Magento status")
                    text = 'Status of Sale order %s  has been successfully updated on Odoo.' % (
                        self.name)
                    status = 'yes'
                    rec.status_updated_on_magento = True
                else:
                    text = 'Magento %s Error for SO %s Error while updating status in odoo' % (api_response, self.name)
                    status = 'no'

                self.env['magento.sync.history'].create(
                    {'status': status, 'action_on': 'order', 'action': 'b', 'error_message': text})
        self.env['magento.sync.history'].create(
            {'status': status, 'action_on': 'order', 'action': 'b', 'error_message': text})

    @api.multi
    def action_confirm(self):
        self.set_tax_on_product()
        res = super(SaleOrder, self).action_confirm()
        if self.eg_magento_payment_method_id.auto_invoice and self.eg_invoice_policy == 'order':
            if self.invoice_ids.filtered(lambda i: i.state == "paid"):
                return res
            invoice_id = self.action_invoice_create()
            invoice_id = self.env["account.invoice"].browse(invoice_id)
            invoice_id.action_invoice_open()
            invoice_id.message_post("Invoice created by system based on auto flow")
            if self.eg_magento_payment_method_id.auto_register:
                invoice_id.pay_and_reconcile(self.eg_magento_payment_method_id.journal_id.id,
                                             pay_amount=invoice_id.residual,
                                             date=self.create_date, writeoff_acc=None)
            invoice_id.message_post("Invoice posted by system based on auto flow")
            inv_template_id = self.env['ir.actions.report']._get_report_from_name(
                'account.report_invoice_with_payments')
            if inv_template_id and self.picking_ids:
                attachments = []
                result = self.picking_ids[0].generate_attachment_of_report(inv_template_id, invoice_id)
                attachments.append((invoice_id.number.replace("/", "_") + '.pdf', result))
                msg = "Invoice {}".format(invoice_id.number)
                self.picking_ids[0].message_post(
                    body=msg,
                    subject="Attachments of Invoice",
                    attachments=attachments
                )
            if self.eg_magento_payment_method_id.register_popup:
                action = self.env.ref('eg_odoo_magento_connect_extended.wizard_action_register_payment_wizard').read()[
                    0]
                return action
        return res

    # @api.multi
    # def custom_action_confirm(self):
    #     self.action_confirm()
    #     action = self.env.ref('eg_odoo_magento_connect_extended.wizard_action_register_payment_wizard').read()[0]
    #     return action

    @api.one
    def manual_magento_order_operation(self, opr):
        if opr in ['shipment', 'invoice']:
            self.update_magento_order_status(opr)
            return []
        else:
            return super(SaleOrder, self).manual_magento_order_operation(opr)

    @api.multi
    def set_tax_product_action(self):
        sale_order_ids = self.browse(self._context.get("active_ids"))
        if sale_order_ids:
            for sale_order_id in sale_order_ids:
                sale_order_id.set_tax_on_product()

    @api.multi
    def get_magento_sale_order(self, method=None):
        for order_id in self:
            if order_id.state == "draft":
                ctx = dict(self._context)
                text = ""
                status = "no"
                mapping_order_id = self.env["wk.order.mapping"].search([("erp_order_id", "=", order_id.id)])
                if mapping_order_id:
                    magento_configure_id = self.env["magento.configure"].search(
                        [("active", "=", True), ("state", "=", "enable")])
                    if magento_configure_id:
                        ctx.update({"instance_id": magento_configure_id.id})
                        connection = self.env["magento.configure"].with_context(ctx)._create_connection()
                        if connection:
                            mag_order_id = mapping_order_id.ecommerce_order_id
                            url = connection[0]
                            token = connection[1]
                            api_url = "{}/rest/V1/orders/{}".format(url, mag_order_id)
                            headers = {'Accept': '*/*', 'Content-Type': 'application/json',
                                       'Authorization': token}
                            try:
                                response = requests.request("GET", url=api_url, headers=headers)

                            except Exception as e:
                                raise Warning("{}".format(e))
                            if response:
                                if response.status_code == 200:
                                    response = json.loads(response.text)
                                    sku_list = []
                                    for order_line_id in order_id.order_line:
                                        sku_list.append(order_line_id.product_id.default_code)
                                    order_line_object = self.env["sale.order.line"]
                                    need_update_from_magento = True
                                    for product in response.get("items"):
                                        sku = product.get("sku")
                                        if sku not in sku_list:
                                            if method == "verify":
                                                order_id.need_update_from_magento = True
                                                return
                                            product_id = self.env["product.product"].search(
                                                [("default_code", "=", sku)])
                                            if product_id:
                                                order_line_object.create({"order_id": order_id.id,
                                                                          "product_id": product_id.id,
                                                                          "product_uom_qty": float(
                                                                              product.get("qty_ordered")),
                                                                          "price_unit": float(
                                                                              product.get("original_price")),
                                                                          "price_total": float(
                                                                              product.get("price_incl_tax")),
                                                                          "purchase_price": float(product.get("price")),
                                                                          "discount": float(
                                                                              product.get("discount_percent")), })
                                                status = "yes"
                                                text = "Success to update sale order : {}".format(order_id.name)
                                                self._cr.commit()

                                            else:
                                                raise Warning(
                                                    "Product does not found in odoo!!! \nProduct : {} \n Internal Ref : {}".format(
                                                        product.get("name"), product.get("sku")))
                                        else:
                                            need_update_from_magento = False
                                    if method == "verify":
                                        order_id.need_update_from_magento = need_update_from_magento
                                        return
                                else:
                                    raise Warning("Magento error: {} while update this sale order: {}".format(
                                        response.text, order_id.name))
                        else:
                            text = "Something went wrong!!!"

                    else:
                        text = "Magento sale order update error for : {} , Could not able to connect magento".format(
                            order_id.name)
                else:
                    raise Warning("No mapping found for order : {}".format(order_id.name))
                self.env['magento.sync.history'].create(
                    {'status': status, 'action_on': 'order', 'action': 'c', 'error_message': text})
                self._cr.commit()
            else:
                raise Warning("Sale order is not in quotation state : {}".format(order_id.name))

    @api.multi
    def verify_sale_order(self):
        sale_order_ids = self.browse(self._context.get("active_ids"))
        for sale_order_id in sale_order_ids:
            try:
                sale_order_id.get_magento_sale_order(method="verify")
            except Exception as e:
                sale_order_id.message_post(body="error occurred while verifying order")

    @api.multi
    def get_remaining_order(self, from_date=None, to_date=None):
        if from_date and to_date:
            ctx = dict(self._context)
            text = ""
            status = "no"
            process = "no"
            partial = False
            partial_1 = False
            magento_configure_id = self.env["magento.configure"].search(
                [("active", "=", True), ("state", "=", "enable")])
            if magento_configure_id:
                ctx.update({"instance_id": magento_configure_id.id})
                connection = self.env["magento.configure"].with_context(ctx)._create_connection()
                if connection:
                    current_date = str(to_date) + " 23:59:59.99"
                    past_date = str(from_date) + " 00:00:00.00"

                    url = connection[0]
                    token = connection[1]
                    api_url = "{}/rest/V1/orders".format(url)
                    headers = {'Accept': '*/*', 'Content-Type': 'application/json',
                               'Authorization': token}
                    querystring = {"searchCriteria[filter_groups][0][filters][0][field]": "created_at",
                                   "searchCriteria[filter_groups][0][filters][0][value]": past_date,
                                   "searchCriteria[filter_groups][0][filters][0][condition_type]": "gteq",
                                   "searchCriteria[filter_groups][1][filters][0][field]": "created_at",
                                   "searchCriteria[filter_groups][1][filters][0][value]": current_date,
                                   "searchCriteria[filter_groups][1][filters][0][condition_type]": "lteq"}
                    try:
                        response = requests.request("GET", url=api_url, headers=headers, params=querystring)

                    except Exception as e:
                        raise Warning("{}".format(e))
                    if response:
                        if response.status_code == 200:
                            response = json.loads(response.text)
                            for order in response.get("items"):
                                mapping_order_id = self.env["wk.order.mapping"].search(
                                    ["|", ("ecommerce_order_id", "=", order.get("entity_id")),
                                     ("name", "=", order.get("increment_id"))])
                                odoo_order_id = self.env["sale.order"].search([("name", "=", order.get("entity_id"))])
                                if not mapping_order_id and odoo_order_id:
                                    self.env["wk.order.mapping"].create({"erp_order_id": odoo_order_id.id,
                                                                         "ecommerce_order_id": order.get(
                                                                             "entity_id"),
                                                                         "order_status": "draft",
                                                                         "ecommerce_channel": "magento",
                                                                         "name": odoo_order_id.name})
                                if not mapping_order_id and not odoo_order_id:
                                    if order.get("customer_is_guest") == 0:
                                        mapping_partner_id = self.env["magento.customers"].search(
                                            [("mag_customer_id", "=", str(order.get("customer_id")))])
                                        if mapping_partner_id:
                                            create_date = datetime.strptime(order.get("created_at"),
                                                                            "%Y-%m-%d %H:%M:%S")
                                            order_id = self.env["sale.order"].create(
                                                {"partner_id": mapping_order_id.oe_customer_id.id,
                                                 "date_order": create_date,
                                                 "name": str(order.get("increment_id"))})
                                            order_id.onchange_partner_id()
                                            order_line_obj = self.env["sale.order.line"]
                                            partial = False
                                            for product in order.get("items"):
                                                mag_product_id = self.env["magento.product"].search(
                                                    [("mag_product_id", "=", product.get("item_id"))])
                                                text = "Product is not mapping, sku:"
                                                if mag_product_id:
                                                    partial_1 = True
                                                    order_line_id = order_line_obj.create(
                                                        {"product_id": mag_product_id.oe_product_id.id,
                                                         "name": product.get("name"),
                                                         "product_uom_qty": product.get("qty_ordered"),
                                                         "price_unit": product.get("price"),
                                                         "order_id": order_id.id,
                                                         "discount": product.get("discount_percent")})
                                                else:
                                                    partial = True
                                                    text = text + ", {}".format(product.get("sku"))
                                            if partial:
                                                text = "Order is successful create but {}".format(text)
                                                process = "partial"
                                            else:
                                                process = "yes"
                                                text = "Successful Order is created"
                                            status = "yes"
                                            self.env["wk.order.mapping"].create({"erp_order_id": order_id.id,
                                                                                 "ecommerce_order_id": order.get(
                                                                                     "entity_id"),
                                                                                 "order_status": "draft",
                                                                                 "ecommerce_channel": "magento",
                                                                                 "name": order_id.name})
                                            self._cr.commit()
                                        else:
                                            text = "Customer is not mapping : {} {}".format(
                                                order.get("customer_firstname"),
                                                order.get("customer_lastname"))
                                            partial = True
                                    else:
                                        text = "Customer is guest so order is not create"

                                self.env["order.history"].create(
                                    {"process": process, "text": text, "name": str(order.get("increment_id")),
                                     "mag_order_id": order.get("entity_id")})
                        else:
                            raise Warning("Magento error for get sale order")
                else:
                    raise Warning("Something went wrong!!! or Check internet connection")
            else:
                raise Warning("Not find the Magento configuration")
            if partial and partial_1:
                text = "Some order create and some order is not create"
            elif partial:
                text = "All order was not created"
            elif partial_1:
                text = "All order was Successful created"

            self.env['magento.sync.history'].create(
                {'status': status, 'action_on': 'order', 'action': 'a', 'error_message': text})
            self.env["order.history"].create({"process": process, "text": text})
            self._cr.commit()

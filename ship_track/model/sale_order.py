# -*- coding: utf-8 -*-
import json
import logging
from datetime import datetime

import requests

from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)


class StockOrder(models.Model):
    _inherit = 'sale.order'

    @api.depends('picking_ids', 'additional_carrier_details')
    def _get_carrier_details(self):
        for order in self:
            text = ''
            for picking in order.picking_ids:
                if picking.carrier_id and picking.carrier_tracking_ref:
                    carrier_id = picking.carrier_id
                    # print(picking.carrier_id.name)
                    # text += str(picking.carrier_id.name) +'-'+ str(picking.carrier_tracking_ref) + ','
                    # Below update by Sahil Navadiya
                    if text != '':
                        text = "%s<br/>" % (text)

                    text += "%s%s" % (carrier_id.tracking_url, picking.carrier_tracking_ref)
            if order.additional_carrier_details:
                text += "---%s" % order.additional_carrier_details
            order.carrier_details = text

    @api.depends('state', 'order_line.invoice_status')
    def _get_payment_method(self):
        for order in self:
            payment_method = ''
            invoice_ids = order.order_line.mapped('invoice_lines').mapped('invoice_id').filtered(
                lambda r: r.type in ['out_invoice', 'out_refund'])
            refunds = invoice_ids.search(
                [('origin', 'like', order.name), ('company_id', '=', order.company_id.id)]).filtered(
                lambda r: r.type in ['out_invoice', 'out_refund'])
            invoice_ids |= refunds.filtered(lambda r: order.name in [origin.strip() for origin in r.origin.split(',')])
            # Search for refunds as well
            refund_ids = self.env['account.invoice'].browse()
            if invoice_ids:
                for inv in invoice_ids:
                    refund_ids += refund_ids.search(
                        [('type', '=', 'out_refund'), ('origin', '=', inv.number), ('origin', '!=', False),
                         ('journal_id', '=', inv.journal_id.id)])
            for invoice in invoice_ids:
                for line in invoice.payment_ids:
                    payment_method += line.journal_id.name
                    payment_method += ','
            order.payment_method = payment_method

    @api.multi
    @api.depends('order_line.qty_delivered', 'order_line.price_unit')
    def _get_fulfilled_amount(self):
        for order in self:
            total = 0
            for line in order.order_line:
                total += (line.qty_delivered * line.price_unit)
            order.fulfilled_amount = total

    ship_track = fields.Char(string="Ship Tracking Number", readonly="True")
    carrier_details = fields.Text('Carrier Details', compute='_get_carrier_details')
    payment_method = fields.Char('Payment Method', compute=_get_payment_method, store=True)
    credit_note_status = fields.Boolean('Is Credit Note', store=True)
    additional_carrier_details = fields.Text('Additional Carrier Details')
    fulfilled_amount = fields.Float('Fulfilled Amount', compute='_get_fulfilled_amount')
    delivery_status_eg = fields.Char("Delivery States", readonly=True)

    # smsa_delivery_status_eg = fields.Char("SMSA Delivery Status")

    @api.multi
    def _prepare_invoice(self):
        res = super(StockOrder, self)._prepare_invoice()
        # if self.payment_gateway_id:
        #     res['payment_gateway_id'] = self.payment_gateway_id.id
        if self.eg_magento_payment_method_id:
            res['eg_magento_payment_method_id'] = self.eg_magento_payment_method_id.id
        return res

    @api.multi
    def action_confirm(self):
        res = super(StockOrder, self).action_confirm()

        for record in self.picking_ids:
            # if self.payment_gateway_id:
            #     record.payment_gateway_id = self.payment_gateway_id.id
            if self.eg_magento_payment_method_id:
                record.eg_magento_payment_method_id = self.eg_magento_payment_method_id.id
        return res

    @api.model
    def cron_register_payment(self):
        # sale_order_ids = self.search(
        #     [('is_delivered', '=', False), '|', ('payment_gateway_id.code', 'ilike', 'cod'),
        #      ('eg_magento_payment_method_id.code', 'ilike', 'cod')])
        sale_order_ids = self.search(
            [('is_delivered', '=', False), ('eg_magento_payment_method_id.code', 'ilike', 'cod')])
        for order in sale_order_ids:
            if order.invoice_ids.filtered(lambda i: i.state == 'paid'):
                order.is_delivered = True
            else:
                order.check_delivery_status_bulk_fl()

    # SAHIL NAVADIYA <navadiyasahil@gmail.com>
    # Invoice payment register if delivery status done
    @api.multi
    def check_delivery_status_bulk_fl(self):
        success_msg = ""
        for so in self:
            # is_cod = so.payment_gateway_id.code in ['cod', 'COD'] or so.eg_magento_payment_method_id.code in [
            #     'cod', 'COD'] or False

            is_cod = so.eg_magento_payment_method_id.code in [
                'cod', 'COD'] or False

            if so.payment_status == "paid" and is_cod:
                continue
            try:
                if so.state != 'sale':
                    continue

                # For COD
                # picking = self.env['stock.picking'].search(
                #     [('sale_id', '=', so.id), ('carrier_tracking_ref', '!=', False),
                #      ('state', 'in', ['done']), '|', ('payment_gateway_id.code', 'in', ['cod', 'COD']),
                #      ('eg_magento_payment_method_id.code', 'in', ['cod', 'COD'])], order="id desc", limit=1)
                picking = self.env['stock.picking'].search(
                    [('sale_id', '=', so.id), ('carrier_tracking_ref', '!=', False), ('state', 'in', ['done'])],
                    order="id desc", limit=1)
                if not picking or not picking.carrier_tracking_ref:
                    continue
                # is_cod = picking.payment_gateway_id.code in ['cod',
                #                                              'COD'] or picking.eg_magento_payment_method_id.code in [
                #              'cod',
                #              'COD'] or False
                if picking.carrier_id.delivery_type == 'saee':
                    track_url = "http://www.saee.sa/tracking?trackingnum="
                    res = requests.get("%s%s" % (track_url, picking.carrier_tracking_ref)).json()
                    _logger.info("=====SAEE PAYMENT REG RES=== {}".format(res))
                    if isinstance(res, dict) and res.get('success') == False:
                        success_msg = "%s\n%s : %s" % (success_msg, so.id, res)
                        continue
                    for del_status in res.get('details'):
                        if del_status.get('status') == 5 and is_cod:
                            is_done = self.pay_and_reconcile_by_so_fl(journal_code='KASPE', so=so, picking=picking)
                            so.is_delivered = is_done
                            break

                elif picking.carrier_id.delivery_type == 'smsa':
                    client = picking.carrier_id.get_smsa_client()
                    if picking.carrier_tracking_ref:
                        tracking_ref_list = picking.carrier_tracking_ref.split(",")
                        for tracking_ref in tracking_ref_list:
                            res = client.service.getStatus(passkey=picking.carrier_id.smsa_pass_key,
                                                           awbNo=tracking_ref)
                            _logger.info("=====SMSA PAYMENT REG RES=== {}".format(res))
                            if res:
                                so.delivery_status_eg = res
                            if res == 'PROOF OF DELIVERY CAPTURED' and is_cod:
                                is_done = self.pay_and_reconcile_by_so_fl(journal_code='SMSA', so=so, picking=picking)
                                so.is_delivered = is_done

                elif picking.carrier_id.delivery_type == 'vaal' and picking.carrier_tracking_ref != 'None':
                    headers = picking.carrier_id.get_vaal_headers()
                    url = "https://deliver.vaal.me/ords/vaal/api/v2/orders/status/%s" % (picking.carrier_tracking_ref)
                    res = requests.get(url, headers=headers).json()
                    _logger.info("=====VAAL PAYMENT REG RES=== {}".format(res))
                    # {'tracking_date': '2020-01-12 10:32:19', 'failed_attempts': 2, 'status_ar': 'مرتجع',
                    # 'status_en': 'Returned', 'order_id': 58320028, 'comments': 'العميل لا يرد'}
                    if isinstance(res, dict) and res.get('success') == False:
                        # raise ValidationError('%s'%res)
                        success_msg = "%s\n%s : %s" % (success_msg, so.id, res)
                        continue
                    if res.get('status_en'):
                        so.delivery_status_eg = res.get('status_en')
                    if res.get('status_en') == 'Delivered' and is_cod:
                        payment_date = datetime.strptime(res.get('tracking_date'), "%Y-%m-%d %H:%M:%S")
                        payment_date = payment_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                        is_done = self.pay_and_reconcile_by_so_fl(journal_code='VAAL', so=so, date=payment_date,
                                                                  picking=picking)
                        so.is_delivered = is_done

                elif picking.carrier_id.delivery_type == 'shipa_delivery' and picking.carrier_tracking_ref != 'None':
                    headers = {
                        'Accept': 'application/json',
                    }

                    params = (
                        ('apikey', picking.carrier_id.shipa_api_key),
                    )
                    url = 'https://api.shipadelivery.com/orders/{}/history'.format(picking.carrier_tracking_ref)
                    response = requests.get(url, headers=headers, params=params).json()
                    _logger.info("=====SHIPA PAYMENT REG RES=== {}".format(response))
                    if response.get("info") == "Success":
                        if isinstance(response.get('history'), list) and len(response.get('history')) > 0:
                            so.delivery_status_eg = response.get('history')[-1].get('code')
                            if response.get('history')[-1].get('code') == 'Package Delivered' and is_cod:
                                datetime_list = response.get('history')[-1].get('time').split(" ")
                                payment_date = datetime.strptime("{} {}".format(datetime_list[0], datetime_list[1]),
                                                                 "%Y-%m-%d %H:%M:%S")
                                payment_date = payment_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                                is_done = self.pay_and_reconcile_by_so_fl(journal_code='SHIPA', so=so,
                                                                          date=payment_date, picking=picking)
                                so.is_delivered = is_done
                elif picking.carrier_id.delivery_type == "Aramex" and picking.carrier_tracking_ref != 'None':
                    try:
                        status = picking.aramex_get_status()
                        so.delivery_status_eg = status
                    except Exception as e:
                        _logger.info(e)
                    #     todo: payment registration
                elif picking.carrier_id.delivery_type == 'clex_delivery' and picking.carrier_tracking_ref != 'None':
                    url = "https://api.clexsa.com/consignment/track-status"
                    headers = {"Content-Type": "application/json",
                               "Access-token": picking.carrier_id.clex_access_token}
                    body = {"shipment_id": picking.carrier_tracking_ref}
                    payload = json.dumps(body)
                    response = requests.request("POST", url, data=payload, headers=headers)

                    if response.status_code == 200:
                        response_dict = json.loads(response.text)
                        _logger.info("=====CLEX RESPONSE=== {}".format(response_dict))
                        if response_dict.get("message") == "Success":
                            # test = {'error': False, 'message': 'Success', 'data': {
                            #     '100000350857': {'warehouse': 'RUH CLEX Station / Al Malaz',
                            #                      'detail': 'Shipment Delivered', 'country_name': '', 'city_name': '',
                            #                      'code': 'SHDL', 'time': '2020-04-22 18:49:59'}}, 'code': 200}
                            data = response_dict.get("data")
                            _logger.info(data)
                            if data and data.get(picking.carrier_tracking_ref) and data.get(picking.carrier_tracking_ref).get(
                                    'detail'):
                                _logger.info(data.get(picking.carrier_tracking_ref).get('detail'))
                                so.delivery_status_eg = data.get(picking.carrier_tracking_ref).get('detail')
                                #     todo: payment registration
                            # if response.get('history')[-1].get('code') == 'Package Delivered':
                            #     datetime_list = response.get('history')[-1].get('time').split(" ")
                            #     payment_date = datetime.strptime("{} {}".format(datetime_list[0], datetime_list[1]),
                            #                                      "%Y-%m-%d %H:%M:%S")
                            #     payment_date = payment_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                            #     is_done = self.pay_and_reconcile_by_so_fl(journal_code='SHIPA', so=so,
                            #                                               date=payment_date, picking=picking)
                            #     so.is_delivered = is_done
            except Exception as e:
                so.message_post(e)
                _logger.info(["=========Error======>>>", e])

        _logger.info("\nAuto Register Invoice Payment Bulk process complete: \n%s", success_msg)

    def pay_and_reconcile_by_so_fl(self, journal_code=None, so=None, date=None, picking=None):
        if so and journal_code:
            is_done = None
            for inv in so.invoice_ids:
                if inv.state == 'open':
                    # To Do: journal_id search should be more accurate, fix it
                    # search_domain = []
                    # if journal_code == 'VAAL':
                    #     search_domain = [('code', '=', 'VAAL')]
                    # elif journal_code == 'SMSA':
                    #     search_domain = [('code', '=', 'SMSA')]
                    # elif journal_code == 'KASPE':
                    #     search_domain = [('code', '=', 'KASPE')]
                    journal_id = self.env['account.journal'].search([('code', '=', journal_code)], limit=1)
                    if journal_id:
                        # def pay_and_reconcile(self, pay_journal, pay_amount=None, date=None, writeoff_acc=None)
                        reg_date = date or picking.date_done
                        is_done = inv.pay_and_reconcile(journal_id.id, pay_amount=inv.residual, date=reg_date,
                                                        writeoff_acc=None)
                        break
            return is_done

    @api.onchange('invoice_count')
    def _onchange_invoices(self):
        if self.invoice_count:
            print(self.invoice_ids)
            for invoice in self.invoice_ids:
                if invoice.type in ['out_refund']:
                    self.credit_note_status = True

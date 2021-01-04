# -*- coding: utf-8 -*-

import logging
import xml.etree.ElementTree as etree

from odoo.addons.aramex_shipping_connector.models.aramex_response import Response
from requests import request

from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # aramex_button_visible = fields.Boolean("Aramex Button Visible", compute='compute_aramex_button', default=False)
    #
    # @api.one
    # @api.depends('order_line')
    # def compute_aramex_button(self):
    #     for rec in self:
    #         if rec.name:
    #             picking = self.env['stock.picking'].search([('sale_id', '=', rec.name),
    #                                                         ('carrier_tracking_ref', '!=', False),
    #                                                         ('state', 'in', ['done']),
    #                                                         ])
    #             rec.aramex_button_visible = False if picking else True
    #         else:
    #             rec.aramex_button_visible = False

    @api.multi
    def send_to_Aramex(self):
        self.ensure_one()
        if self.name is False:
            raise ValidationError('Source Document is not set!')

        # Selecting only last created picking/DO
        picking = self.env['stock.picking'].search([('sale_id', '=', self.id),
                                                    ('carrier_tracking_ref', '=', False),
                                                    ('state', 'not in', ['cancel'])], order="id desc", limit=1)

        if len(picking) > 1:
            raise ValidationError(
                'Multiple delivery order found for source document : %s, Please cancel all and create one!' % (
                    self.name))

        elif picking:
            carrier_id = self.env['delivery.carrier'].search([('delivery_type', '=', 'Aramex')], limit=1)
            picking.carrier_id = carrier_id.id
            # picking.write({'carrier_id':carrier_id.id, 'cod_amount':invoice.residual})
            return picking.with_context(carrier_id='Aramex').button_validate()
        else:
            raise ValidationError('No valid delivery order found for source document : %s' % (self.name))
        # else:
        #    raise ValidationError('No open invoice found for sale order : %s'%(self.name))

    @api.multi
    def aramex_check_delivery_status(self):
        self.ensure_one()
        picking = self.env['stock.picking'].search([('sale_id', '=', self.name), ('carrier_tracking_ref', '!=', False),
                                                    ('state', 'in', ['done']),
                                                    ('carrier_id.delivery_type', '=', 'Aramex'),
                                                    # ('payment_gateway_id.code', 'in', ['cod', 'COD'])
                                                    ],
                                                   order="id desc",
                                                   limit=1)
        if picking:
            root_node = etree.Element("Envelope")
            root_node.attrib['xmlns'] = "http://schemas.xmlsoap.org/soap/envelope/"

            Body = etree.SubElement(root_node, "Body")
            # <body><ShipmentCreationRequest>
            ShipmentTrackingRequest = etree.SubElement(Body, "ShipmentTrackingRequest")
            ShipmentTrackingRequest.attrib['xmlns'] = "http://ws.aramex.net/ShippingAPI/v1/"

            ClientInfo = etree.SubElement(ShipmentTrackingRequest, "ClientInfo")
            etree.SubElement(ClientInfo, "UserName").text = self.carrier_id.aramex_username or ''
            etree.SubElement(ClientInfo, "Password").text = self.carrier_id.aramex_password or ''
            etree.SubElement(ClientInfo, "Version").text = self.carrier_id.aramex_version or ''
            etree.SubElement(ClientInfo, "AccountNumber").text = self.carrier_id.aramex_account_number or ''
            etree.SubElement(ClientInfo, "AccountPin").text = self.carrier_id.aramex_account_pin or ''
            etree.SubElement(ClientInfo, "AccountEntity").text = self.carrier_id.aramex_account_entity or ''
            etree.SubElement(ClientInfo,
                             "AccountCountryCode").text = self.company_id.country_id.code or ''

            Shipments = etree.SubElement(ShipmentTrackingRequest, "Shipments")
            etree.SubElement(Shipments, "string", attrib={
                'xmlns': "http://schemas.microsoft.com/2003/10/Serialization/Arrays"}).text = picking.carrier_tracking_ref
            etree.SubElement(ShipmentTrackingRequest, "GetLastTrackingUpdateOnly").text = "true"

            url = "http://ws.aramex.net/shippingapi/tracking/service_1_0.svc"
            headers = {"Content-Type": "text/xml; charset=utf-8",
                       "SOAPAction": "http://ws.aramex.net/ShippingAPI/v1/Service_1_0/TrackShipments"}
            body = etree.tostring(root_node).decode('utf-8')
            _logger.info("aramex Shipment Requesting Data: %s" % (body))
            res = request(method='POST', url=url, headers=headers, data=body)

            if res.status_code == 200:
                api = Response(res)
                results = api.dict()
                _logger.info("aramex Shipment Response Data : %s" % (results))
                product_details = results.get('Envelope', {}).get('Body', {}).get('ShipmentTrackingResponse', {})
                haserror = product_details.get('HasErrors')
                if haserror != 'false':
                    raise ValidationError('%s' % results)

                tracking_status = product_details.get('TrackingResults', {}).get(
                    'KeyValueOfstringArrayOfTrackingResultmFAkxlpY', {}).get('Value', {})
                status = tracking_status.get('TrackingResult', {}).get('UpdateDescription', {})
                if status == 'Delivered':
                    for inv in self.invoice_ids:
                        if inv.state == 'open':
                            # To Do: journal_id search should be more accurate, fix it
                            journal_id = self.env['account.journal'].search([('code', '=', 'Aramex')], limit=1)
                            if journal_id:
                                # def pay_and_reconcile(self, pay_journal, pay_amount=None, date=None, writeoff_acc=None)
                                inv.pay_and_reconcile(journal_id.id, pay_amount=inv.residual, date=None,
                                                      writeoff_acc=None)
                                break
                else:
                    print(status)
            # raise ValidationError(delivery_status.get(del_status.get('status')))
        # res.raise_for_status()

    def aramex_return_send_shipping(self):
        aramex_id = self.env['delivery.carrier'].search([('delivery_type', '=', 'Aramex')])
        if aramex_id:
            aramex_id.aramex_return_send_shipping(self)
        else:
            raise ValidationError("Aramex not found")

    def aramex_send_return_label_to_customer(self):
        if self.partner_id.email:
            msg = "اهلين {}        مرفق بوليصة الشحن للاسترجع            فريق بيتونيا                  baytonia.com".format(
                self.partner_id.name)
            values = {
                'model': 'sale.order',
                'res_id': self.id,
                'subject': "Return shipment label",
                'body': "",
                'body_html': msg,
                'parent_id': None,
                'attachment_ids': [(6, 0, self.return_label_attachment_id.ids)] or None,
                'email_from': "wecare@baytonia.com",
                'email_to': self.partner_id.email,
                'email_cc': "wecare@baytonia.com,Enriquejr@aramex.com,tariqd@aramex.com",
            }
            mail_id = self.env['mail.mail']
            mail_id.create(values).send()

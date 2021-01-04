import base64
import binascii
import logging
import time
import xml.etree.ElementTree as etree

import regex
import requests
from odoo.addons.aramex_shipping_connector.models.aramex_response import Response
from requests import request

from odoo import models, fields, api, _
from odoo.exceptions import Warning

_logger = logging.getLogger(__name__)


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"
    delivery_type = fields.Selection(selection_add=[("Aramex", "Aramex")])

    aramex_username = fields.Char(string="Aramex UserId", copy=False,
                                  help="A unique user name sent to the customer upon registration with http://www.aramex.com")
    aramex_password = fields.Char(string="Aramex Password", copy=False,
                                  help="A unique password to verify the user name, sent to the client upon registration with http://www.aramex.com")
    aramex_version = fields.Char(string="Aramex version", copy=False,
                                 help="Based on the WSDL the customer is using to invoke the web service")
    aramex_account_number = fields.Char(string="Account Number",
                                        help="The Customer’s Account number provided by Aramex when the contract is signed.")
    aramex_account_pin = fields.Char(string="Account PIN",
                                     help="A key that is given to account customers associated with the account number, so as to validate customer identity.")
    aramex_account_entity = fields.Char(string="Account Entity", copy=False,
                                        help="Identification Code/Number for Transmitting Party. This code should be provided to you by Aramex. ")

    aramex_service_type = fields.Selection([('OND', 'OND - Non-Document'),
                                            ('PDX', 'PDX - Priority Document Express'),
                                            ('PPX', 'PPX - Priority Parcel Express'),
                                            ('PLX', 'PLX - Priority Letter Express'),
                                            ('DDX', 'DDX - Deferred Document Express'),
                                            ('DPX', 'DPX - Deferred Parcel Express'),
                                            ('GDX', 'GDX - Ground Document Express'),
                                            ('GPX', 'GPX - Ground Parcel Express'),
                                            ('EPX', 'EPX - Economy Parcel Express')],
                                           string="Service Type", default='OND',
                                           help="Product Type involves the specification of certain features concerning the delivery of the product such as: Priority, Time Sensitivity, and whether it is a Document or Non-Document.")
    aramex_product_group = fields.Selection([('EXP', 'EXP - Express'), ('DOM', 'DOM - Domestic')],
                                            string="Aramex Product Group", default='DOM',
                                            help="Shipping Services those are accepted by Aramex")
    aramex_weight_uom = fields.Selection([('LB', 'LBS-Pounds'), ('KG', 'KGS-Kilograms')], default='KG',
                                         string="Weight UOM", help="Weight UOM of the Shipment")
    aramex_unit = fields.Selection([('CM', 'CM - Centimeter '), ('M', 'M - Meter')], default='CM', string="Unit",
                                   help="Measurement Unit, If any of the Dimensional values are filled then the rest must be filled. ")
    aramex_payment_type = fields.Selection([('P', 'P - Prepaid'), ('C', 'C - Collect'), ('3', '3-Third-party')],
                                           string="Aramex Payment Type",
                                           default="P",
                                           help="Payment type Shipping Services those are accepted by Aramex")
    aramex_payment_options = fields.Selection([('CASH', 'CASH - Cash'),
                                               ('ACCT', 'ACCT - Account'),
                                               ('PPST', 'PPST - Prepaid Stock'),
                                               ('CRDT', 'CRDT - Credit'),
                                               ('ASCC', 'ASCC - Needs Shipper Account Number to be filled'),
                                               ('ARCC', 'ARCC - Needs Consignee Account Number to be filled')],
                                              string="Aramex Payment Option", default="CASH",
                                              help="Payment option Shipping Services those are accepted by Aramex")
    aramex_services = fields.Selection([('CODS', 'CODS - Cash on Delivery'),
                                        ('FIRST', 'FIRST - First Delivery'),
                                        ('FRDOM', 'FRDOM - Free Domicile'),
                                        ('HFPU', 'HFPU  - Hold for pick up'),
                                        ('NOON', 'NOON - Noon Delivery'),
                                        ('SIG', 'SIG - Signature Required')],
                                       string="Aramex Services",
                                       help="Payment option Shipping Services those are accepted by Aramex")

    # aramex_insurance_amount=fields.Boolean(string="Insurance Amount",help="Insurance Amount charged on shipment")
    # aramex_customs_value = fields.Boolean(string="Customs Value", help="Value Charged by Destination Customs. Conditional - Based on the ProductType Dutible.(PPX, DPX, GPX, EPX)")
    is_fixed_price = fields.Boolean(string="Is Fixed price", default=False, help="set fixed amount")
    fixed_amount = fields.Float(string="Fixed Amount", help="set fixed amount")

    @api.model
    def get_aramex_url(self, url_data):

        return "http://ws.aramex.net/ShippingAPI.V2%s" % (
            url_data) if self.prod_environment else "http://ws.dev.aramex.net/ShippingAPI.V2%s" % (url_data)

    @api.multi
    def body_request_for_aramex_rate_calculation(self, shipper_address, recipient_address, total_weight, description,
                                                 payment_option):

        root_node = etree.Element("Envelope")
        root_node.attrib['xmlns'] = "http://schemas.xmlsoap.org/soap/envelope/"
        body = etree.SubElement(root_node, "Body")

        RateCalculatorRequest = etree.SubElement(body, "RateCalculatorRequest")
        RateCalculatorRequest.attrib['xmlns'] = "http://ws.aramex.net/ShippingAPI/v1/"

        ClientInfo = etree.SubElement(RateCalculatorRequest, "ClientInfo")
        etree.SubElement(ClientInfo, "UserName").text = self.aramex_username or ''
        etree.SubElement(ClientInfo, "Password").text = self.aramex_password or ''
        etree.SubElement(ClientInfo, "Version").text = self.aramex_version or ''
        etree.SubElement(ClientInfo, "AccountNumber").text = ''
        etree.SubElement(ClientInfo, "AccountPin").text = self.aramex_account_pin or ''
        etree.SubElement(ClientInfo, "AccountEntity").text = self.aramex_account_entity or ''
        etree.SubElement(ClientInfo,
                         "AccountCountryCode").text = shipper_address.country_id and shipper_address.country_id.code or ''

        OriginAddress = etree.SubElement(RateCalculatorRequest, 'OriginAddress')
        etree.SubElement(OriginAddress, "Line1").text = shipper_address.street or ''
        etree.SubElement(OriginAddress, "Line2").text = shipper_address.street2 or ''
        etree.SubElement(OriginAddress, "Line3").text = ''
        etree.SubElement(OriginAddress, "City").text = shipper_address.city or ''
        etree.SubElement(OriginAddress,
                         "StateOrProvinceCode").text = shipper_address.state_id and shipper_address.state_id.name or ''
        etree.SubElement(OriginAddress, "PostCode").text = shipper_address.zip or ''
        etree.SubElement(OriginAddress,
                         "CountryCode").text = shipper_address.country_id and shipper_address.country_id.code or ''

        DestinationAddress = etree.SubElement(RateCalculatorRequest, 'DestinationAddress')
        etree.SubElement(DestinationAddress, "Line1").text = recipient_address.street or ''
        etree.SubElement(DestinationAddress, "Line2").text = recipient_address.street2 or ''
        etree.SubElement(DestinationAddress, "Line3").text = ''
        etree.SubElement(DestinationAddress, "City").text = recipient_address.city or ''
        etree.SubElement(DestinationAddress,
                         "StateOrProvinceCode").text = recipient_address.state_id and shipper_address.state_id.name or ''
        etree.SubElement(DestinationAddress, "PostCode").text = recipient_address.zip or ''
        etree.SubElement(DestinationAddress,
                         "CountryCode").text = recipient_address.country_id and recipient_address.country_id.code or ''

        ShipmentDetails = etree.SubElement(RateCalculatorRequest, 'ShipmentDetails')

        Dimensions = etree.SubElement(ShipmentDetails, 'Dimensions')
        etree.SubElement(Dimensions, 'Length').text = "10"
        etree.SubElement(Dimensions, 'Width').text = "10"
        etree.SubElement(Dimensions, 'Height').text = "10"
        etree.SubElement(Dimensions, 'Unit').text = self.aramex_unit or "CM"

        # <RateCalculatorRequest>/<ShipmentDetails><ActualWeight>
        ActualWeight = etree.SubElement(ShipmentDetails, 'ActualWeight')
        etree.SubElement(ActualWeight, 'Unit').text = "%s" % (self.aramex_weight_uom)
        etree.SubElement(ActualWeight, 'Value').text = str(total_weight)

        # <RateCalculatorRequest>/<ShipmentDetails><Dimensions>
        ChargeableWeight = etree.SubElement(ShipmentDetails, 'ChargeableWeight')
        etree.SubElement(ChargeableWeight, 'Unit').text = "%s" % (self.aramex_weight_uom)
        etree.SubElement(ChargeableWeight, 'Value').text = "%s" % (total_weight)
        etree.SubElement(ShipmentDetails, 'DescriptionOfGoods').text = "%s" % (description or '')
        etree.SubElement(ShipmentDetails,
                         'GoodsOriginCountry').text = shipper_address.country_id and shipper_address.country_id.code or ''
        etree.SubElement(ShipmentDetails, 'NumberOfPieces').text = "1" or ''
        etree.SubElement(ShipmentDetails, 'ProductGroup').text = self.aramex_product_group or ''
        etree.SubElement(ShipmentDetails, 'ProductType').text = self.aramex_service_type or ''
        etree.SubElement(ShipmentDetails, 'PaymentType').text = self.aramex_payment_type or ''
        etree.SubElement(ShipmentDetails, 'PaymentOptions').text = payment_option or ''
        if self.aramex_payment_options == 'CASH' or payment_option == 'CASH':
            etree.SubElement(ShipmentDetails, 'Services').text = 'CODS' or ''
        etree.SubElement(ShipmentDetails, 'Services').text = self.aramex_services or ''

        return etree.tostring(root_node).decode('utf-8')

    @api.multi
    def aramex_get_rate_shipment(self, shipper_address, recipient_address, total_weight, description, payment_option):

        self.ensure_one()
        try:
            headers = {"Content-Type": "text/xml; charset=utf-8",
                       "SOAPAction": "http://ws.aramex.net/ShippingAPI/v1/Service_1_0/CalculateRate"}
            body = self.body_request_for_aramex_rate_calculation(shipper_address, recipient_address, total_weight,
                                                                 description, payment_option)
            _logger.info("Aramex Rate Requesting Data: %s" % (body))
            url = self.get_aramex_url("/RateCalculator/Service_1_0.svc")
            response_body = request(method='POST', url=url, headers=headers, data=body)
            if response_body.status_code == 200:
                api = Response(response_body)
                results = api.dict()
                _logger.info("Aramex Rate Response Data : %s" % (results))
                product_details = results.get('Envelope', {}).get('Body', {}).get('RateCalculatorResponse', {}) or False
                service_detail = product_details.get('TotalAmount', {})
                shipment_charge = service_detail.get('Value', False)
                notification = product_details.get('Notifications')
                haserror = product_details.get('HasErrors')
                if haserror == 'false':
                    return {'success': True, 'price': float(shipment_charge), 'error_message': False,
                            'warning_message': False}
                else:
                    error_details = notification
            else:
                error_details = "%s" % (response_body)
        except Exception as e:
            error_details = e
        return {'success': False, 'price': 0.0, 'error_message': error_details, 'warning_message': False}

    @api.multi
    def Aramex_rate_shipment(self, order):

        if order.carrier_id.free_over:
            return {'success': False, 'price': 0.0, 'error_message': "", 'warning_message': False}
        elif self.is_fixed_price:
            return {'success': False, 'price': self.fixed_amount, 'error_message': "", 'warning_message': False}

        if order.eg_magento_payment_method_id.code in ['cod', 'COD']:
            payment_option = "CASH"
        else:
            payment_option = self.aramex_payment_options

        shipper_address = order.company_id
        recipient_address = order.partner_id

        cCity = recipient_address.city

        # text = "aweer wqمرحباмир"
        final_city = ""
        for t in cCity.split():
            result = regex.sub(u'[^\p{Latin}]', u'', t)
            if final_city:
                final_city = final_city + " " + result
            else:
                final_city = result
        recipient_address.city = final_city

        total_weight = sum(
            [(line.product_id.weight * line.product_uom_qty) for line in order.order_line if
             not line.is_delivery]) or 10
        description = ','.join(
            [order_line.product_id and order_line.product_id.name for order_line in order.order_line])
        shipping_dict = self.aramex_get_rate_shipment(shipper_address, recipient_address, total_weight,
                                                      description or '', payment_option)
        return shipping_dict

    @api.multi
    def body_request_for_aramex_send_shipping(self, picking, picking_company_id, picking_partner_id, total_value,
                                              total_bulk_weight, extra_price, payment_option, return_shipment=None):

        root_node = etree.Element("Envelope")
        root_node.attrib['xmlns'] = "http://schemas.xmlsoap.org/soap/envelope/"

        body = etree.SubElement(root_node, "Body")
        # <body><ShipmentCreationRequest>
        ShipmentCreationRequest = etree.SubElement(body, "ShipmentCreationRequest")
        ShipmentCreationRequest.attrib['xmlns'] = "http://ws.aramex.net/ShippingAPI/v1/"

        # <body><ShipmentCreationRequest><ClientInfo>
        ClientInfo = etree.SubElement(ShipmentCreationRequest, "ClientInfo")
        etree.SubElement(ClientInfo, "UserName").text = self.aramex_username or ''
        etree.SubElement(ClientInfo, "Password").text = self.aramex_password or ''
        etree.SubElement(ClientInfo, "Version").text = self.aramex_version or ''
        etree.SubElement(ClientInfo, "AccountNumber").text = self.aramex_account_number or ''
        etree.SubElement(ClientInfo, "AccountPin").text = self.aramex_account_pin or ''
        etree.SubElement(ClientInfo, "AccountEntity").text = self.aramex_account_entity or ''
        etree.SubElement(ClientInfo,
                         "AccountCountryCode").text = picking_company_id.country_id and picking_company_id.country_id.code or ''

        # <body><ShipmentCreationRequest><Shipments>
        Shipments = etree.SubElement(ShipmentCreationRequest, "Shipments")
        for package_id in picking.package_ids:
            product_weight = package_id.shipping_weight
            description = ','.join([move_line_id.product_id.name for move_line_id in package_id.move_line_ids])
            self.request_for_shipment_body_aramex_send_shipping(Shipments, product_weight, picking_company_id,
                                                                picking_partner_id, description or '', total_value,
                                                                extra_price, payment_option, picking, return_shipment)
        if total_bulk_weight:
            description = ','.join(
                [move_line_id.product_id.name if not move_line_id.result_package_id else '' for move_line_id in
                 picking.move_line_ids])
            self.request_for_shipment_body_aramex_send_shipping(Shipments, total_bulk_weight, picking_company_id,
                                                                picking_partner_id, description, total_value,
                                                                extra_price, payment_option, picking, return_shipment)

        LabelInfo = etree.SubElement(ShipmentCreationRequest, 'LabelInfo')
        etree.SubElement(LabelInfo, 'ReportID').text = '9729'
        etree.SubElement(LabelInfo, 'ReportType').text = 'RPT'

        return etree.tostring(root_node).decode('utf-8')

    @api.multi
    def request_for_shipment_body_aramex_send_shipping(self, Shipments, product_weight, picking_company_id,
                                                       picking_partner_id, description, total_value, extra_price,
                                                       payment_option, picking, return_shipment=None):

        Shipment = etree.SubElement(Shipments, "Shipment")
        etree.SubElement(Shipment, "Reference1").text = picking.origin
        Shipper = etree.SubElement(Shipment, "Shipper")
        etree.SubElement(Shipper, "AccountNumber").text = self.aramex_account_number or ''
        # etree.SubElement(Shipper, "R").text = self.aramex_account_number or ''

        PartyAddress = etree.SubElement(Shipper, "PartyAddress")
        if not picking_company_id.street:
            raise Warning("please enter Shipper street")
        etree.SubElement(PartyAddress, "Line1").text = picking_company_id.street or ''
        etree.SubElement(PartyAddress, "Line2").text = picking_company_id.street2 or ''
        etree.SubElement(PartyAddress, "Line3").text = picking_company_id.street2 or ''
        if not picking_company_id.city:
            raise Warning("please enter Shipper city")
        etree.SubElement(PartyAddress, "City").text = picking_company_id.city or ''
        if not picking_company_id.state_id:
            raise Warning("please enter Shipper state")
        etree.SubElement(PartyAddress,
                         "StateOrProvinceCode").text = picking_company_id.state_id and picking_company_id.state_id.name or ''
        etree.SubElement(PartyAddress, "PostCode").text = picking_company_id.zip or ''
        if not picking_company_id.country_id:
            raise Warning("please enter Shipper country")
        etree.SubElement(PartyAddress,
                         "CountryCode").text = picking_company_id.country_id and picking_company_id.country_id.code or ''

        Contact = etree.SubElement(Shipper, "Contact")
        etree.SubElement(Contact, "PersonName").text = picking_company_id.name or ''
        etree.SubElement(Contact, "CompanyName").text = picking_company_id.name or ''
        shipper_phone = picking_company_id.phone or return_shipment and picking_company_id.mobile
        if not shipper_phone and return_shipment:
            shipper_phone = picking.sale_id.partner_shipping_id.phone or picking.sale_id.partner_shipping_id.mobile
        if not shipper_phone:
            raise Warning("please enter Shipper phone")
        etree.SubElement(Contact, "PhoneNumber1").text = shipper_phone or ''
        etree.SubElement(Contact, "PhoneNumber2").text = shipper_phone or ''
        etree.SubElement(Contact, "CellPhone").text = shipper_phone or ''
        if not picking_company_id.email:
            raise Warning("please enter Shipper email")
        etree.SubElement(Contact, "EmailAddress").text = picking_company_id.email or ''
        etree.SubElement(Contact, "Type").text = ''

        Consignee = etree.SubElement(Shipment, "Consignee")

        PartyAddress1 = etree.SubElement(Consignee, "PartyAddress")
        if not picking_partner_id.street:
            raise Warning("please enter Receiver street")
        etree.SubElement(PartyAddress1, "Line1").text = picking_partner_id.street or ''
        etree.SubElement(PartyAddress1, "Line2").text = picking_partner_id.street2 or ''
        etree.SubElement(PartyAddress1, "Line3").text = picking_partner_id.street2 or ''
        if not picking_partner_id.city:
            raise Warning("please enter Receiver city")
        etree.SubElement(PartyAddress1, "City").text = picking_partner_id.city or ''
        if not picking_partner_id.state_id:
            raise Warning("please enter Receiver state")
        etree.SubElement(PartyAddress1,
                         "StateOrProvinceCode").text = picking_partner_id.state_id and picking_partner_id.state_id.name or ''
        # if not picking_partner_id.zip:
        #     raise Warning("please enter Receiver zip")
        etree.SubElement(PartyAddress1, "PostCode").text = picking_partner_id.zip or "21589"
        if not picking_partner_id.country_id:
            raise Warning("please enter Receiver country")
        etree.SubElement(PartyAddress1,
                         "CountryCode").text = picking_partner_id.country_id and picking_partner_id.country_id.code or ''

        # <body><ShipmentCreationRequest><Shipments><Shipment><Consignee><Contact1>
        Contact1 = etree.SubElement(Consignee, "Contact")
        etree.SubElement(Contact1, "PersonName").text = picking_partner_id.name or ''
        etree.SubElement(Contact1, "CompanyName").text = picking_partner_id.name or ''
        if not picking_partner_id.phone:
            raise Warning("please enter Receiver phone number")
        etree.SubElement(Contact1, "PhoneNumber1").text = picking_partner_id.phone or ''
        etree.SubElement(Contact1, "PhoneNumber2").text = picking_partner_id.phone or ''
        if not picking_partner_id.phone:
            raise Warning("please enter Receiver phone")
        etree.SubElement(Contact1, "CellPhone").text = picking_partner_id.phone or ''
        if not picking_partner_id.email:
            raise Warning("please enter Receiver email")
        etree.SubElement(Contact1, "EmailAddress").text = picking_partner_id.email or ''
        etree.SubElement(Contact1, "Type").text = ''
        if self.aramex_payment_type == '3':
            ThirdParty = etree.SubElement(Shipment, "ThirdParty")
            etree.SubElement(ThirdParty, "Reference1").text = "test"
            etree.SubElement(ThirdParty, "Reference2").text = "test"
            etree.SubElement(ThirdParty, "AccountNumber").text = self.aramex_account_number or ''

            PartyAddress = etree.SubElement(ThirdParty, "PartyAddress")
            etree.SubElement(PartyAddress, "Line1").text = picking_company_id.street or ''
            etree.SubElement(PartyAddress, "Line2").text = picking_company_id.street2 or ''
            etree.SubElement(PartyAddress, "Line3").text = picking_company_id.street2 or ''
            etree.SubElement(PartyAddress, "City").text = picking_company_id.city or ''
            etree.SubElement(PartyAddress,
                             "StateOrProvinceCode").text = picking_company_id.state_id and picking_company_id.state_id.name or ''
            etree.SubElement(PartyAddress, "PostCode").text = picking_company_id.zip or ''
            etree.SubElement(PartyAddress,
                             "CountryCode").text = picking_company_id.country_id and picking_company_id.country_id.code or ''

            Contact = etree.SubElement(ThirdParty, "Contact")
            etree.SubElement(Contact, "PersonName").text = picking_company_id.name or ''
            etree.SubElement(Contact, "CompanyName").text = picking_company_id.name or ''
            etree.SubElement(Contact, "PhoneNumber1").text = shipper_phone or ''
            etree.SubElement(Contact, "PhoneNumber2").text = shipper_phone or ''
            etree.SubElement(Contact, "CellPhone").text = shipper_phone or ''
            etree.SubElement(Contact, "EmailAddress").text = picking_company_id.email or ''
            etree.SubElement(Contact, "Type").text = ''

        current_date = time.strftime('%Y-%m-%dT%H:%M:%S')
        etree.SubElement(Shipment, "ShippingDateTime").text = "%s" % (current_date)
        etree.SubElement(Shipment, "DueDate").text = "%s" % (current_date)

        Details = etree.SubElement(Shipment, 'Details')

        Dimensions = etree.SubElement(Details, 'Dimensions')
        etree.SubElement(Dimensions, 'Length').text = "10"
        etree.SubElement(Dimensions, 'Width').text = "10"
        etree.SubElement(Dimensions, 'Height').text = "10"
        etree.SubElement(Dimensions, 'Unit').text = self.aramex_unit or ''

        ActualWeight = etree.SubElement(Details, 'ActualWeight')
        etree.SubElement(ActualWeight, 'Unit').text = "%s" % (self.aramex_weight_uom)
        etree.SubElement(ActualWeight, 'Value').text = str(product_weight)

        ChargeableWeight = etree.SubElement(Details, 'ChargeableWeight')
        etree.SubElement(ChargeableWeight, 'Unit').text = "%s" % (self.aramex_weight_uom)
        etree.SubElement(ChargeableWeight, 'Value').text = str(product_weight)

        etree.SubElement(Details, 'DescriptionOfGoods').text = "%s" % (description or '')
        etree.SubElement(Details,
                         'GoodsOriginCountry').text = picking_company_id.country_id and picking_company_id.country_id.code or ''
        etree.SubElement(Details, 'NumberOfPieces').text = str(picking.boxes)
        etree.SubElement(Details, 'ProductGroup').text = self.aramex_product_group or ''
        etree.SubElement(Details, 'ProductType').text = "CDS"  # self.aramex_service_type or ''
        etree.SubElement(Details, 'PaymentType').text = self.aramex_payment_type or ''
        etree.SubElement(Details, 'PaymentOptions').text = ''  # payment_option or ''

        if self.aramex_payment_options == 'CASH' or payment_option == 'CASH':
            CashOnDeliveryAmount = etree.SubElement(Details, "CashOnDeliveryAmount")
            etree.SubElement(CashOnDeliveryAmount,
                             'CurrencyCode').text = picking_company_id.currency_id and picking_company_id.currency_id.name or ''
            etree.SubElement(CashOnDeliveryAmount, 'Value').text = "%s" % (total_value + extra_price or '')
            etree.SubElement(Details, 'Services').text = 'CODS' or ''
        else:
            etree.SubElement(Details, 'Services').text = self.aramex_services or ''

        return etree.tostring(Shipments).decode('utf-8')

    @api.model
    def Aramex_send_shipping(self, pickings):

        self.ensure_one()
        response = []
        for picking in pickings:
            if picking.sale_id.eg_magento_payment_method_id.code in ['cod', 'COD']:
                payment_option = "CASH"
            else:
                payment_option = self.aramex_payment_options

            # for line in picking.move_line_ids:
            #     if not line.product_id.weight and line.product_id.type != "service":
            #         raise Warning("please enter weight for product: %s" % str(line.product_id.name))
            total_value = 0.0
            if picking.sale_id.eg_magento_payment_method_id.code in ['cod', 'COD']:
                if not picking.invoice_id:
                    raise Warning("Invoice not found!!!")
                total_value = picking.invoice_id.amount_total

            total_weight = picking.shipping_weight
            # total_value = sum([(line.product_uom_qty * line.product_id.list_price) for line in picking.move_lines])
            total_bulk_weight = 10  # picking.weight_bulk
            list_name = []
            for product_list in picking.move_lines:
                list_name.append(product_list.product_id.name)
            product_name = ','.join(list_name)
            picking_partner_id = picking.partner_id
            picking_company_id = picking.company_id

            cCity = picking_partner_id.city

            # text = "aweer wqمرحباмир"
            final_city = ""
            for t in cCity.split():
                result = regex.sub(u'[^\p{Latin}]', u'', t)
                if final_city:
                    final_city = final_city + " " + result
                else:
                    final_city = result
            picking_partner_id.city = final_city

            # if picking.carrier_id.free_over and self.sale_id:
            extra_price = 0.0
            # elif self.is_fixed_price:
            #     extra_price = self.fixed_amount
            # else:
            #     res = self.aramex_get_rate_shipment(picking_company_id, picking_partner_id, total_weight, product_name,
            #                                         payment_option)
            #     extra_price = res.get('price') if res.get('success') else 0.0
            try:
                headers = {"Content-Type": "text/xml; charset=utf-8",
                           "SOAPAction": "http://ws.aramex.net/ShippingAPI/v1/Service_1_0/CreateShipments"}
                body = self.body_request_for_aramex_send_shipping(picking, picking_company_id, picking_partner_id,
                                                                  total_value, total_bulk_weight, extra_price,
                                                                  payment_option)
                _logger.info("aramex Shipment Requesting Data: %s" % (body))
                url = self.get_aramex_url("/Shipping/Service_1_0.svc")
                response_body = request(method='POST', url=url, headers=headers, data=body)
                if response_body.status_code == 200:
                    api = Response(response_body)
                    results = api.dict()
                    _logger.info("aramex Shipment Response Data : %s" % (results))
                    product_details = results.get('Envelope', {}).get('Body', {}) and results.get('Envelope', {}).get(
                        'Body', {}).get('ShipmentCreationResponse', {}) or False
                    processed_shipment = product_details and product_details.get('Shipments',
                                                                                 {}) and product_details.get(
                        'Shipments', {}).get('ProcessedShipment', {}) or False
                    haserror = product_details and product_details.get('HasErrors')
                    final_tracking_no = []
                    if haserror == 'false' and processed_shipment:
                        if isinstance(processed_shipment, dict):
                            processed_shipment = [processed_shipment]
                        for detail in processed_shipment:
                            label_detail = detail.get('ShipmentLabel', {}) and detail.get('ShipmentLabel', {}).get(
                                'LabelFileContents', {})
                            tracking_no = detail.get('ID', {})
                            if detail.get('ShipmentAttachments', {}):
                                commercial_invloce = detail.get('ShipmentAttachments', {}) and detail.get(
                                    'ShipmentAttachments', {}).get('ProcessedShipmentAttachment', {}) and detail.get(
                                    'ShipmentAttachments', {}).get('ProcessedShipmentAttachment', {}).get('Url', {})
                                if commercial_invloce:
                                    pdf_converter = binascii.a2b_base64(
                                        (base64.b64encode(requests.get(commercial_invloce).content)).decode('utf-8'))
                                    mesage_obj = ("Commercial Invoice Generated ")
                                    if picking.sale_id:
                                        picking.sale_id.message_post(body=mesage_obj, attachments=[
                                            ('Aramex Commercial Invoice_%s.pdf' % (tracking_no), pdf_converter)])
                                    picking.message_post(body=mesage_obj, attachments=[
                                        ('Aramex Commercial Invoice_%s.pdf' % (tracking_no), pdf_converter)])
                            form_binary_data = binascii.a2b_base64(str(label_detail))
                            mesage_obj = (_("Shipment created!<br /> <b>Shipment Tracking Number : </b>%s") % (
                                tracking_no))
                            if picking.sale_id:
                                picking.sale_id.message_post(body=mesage_obj, attachments=[
                                    ('Aramex Label Form_%s.pdf' % (tracking_no), form_binary_data)])
                            picking.message_post(body=mesage_obj, attachments=[
                                ('Aramex Label Form_%s.pdf' % (tracking_no), form_binary_data)])
                            final_tracking_no.append(tracking_no)
                            shipping_data = {'exact_price': extra_price, 'tracking_number': ','.join(final_tracking_no)}
                            response = [shipping_data]
                        return response
                    else:
                        raise Warning(results)
                else:
                    raise Warning(response_body.text)
            except Exception as e:
                raise Warning(e)

    @api.multi
    def Aramex_get_tracking_link(self, picking):

        link = 'https://www.aramex.com/track/results?ShipmentNumber='
        res = '%s%s' % (link, picking.carrier_tracking_ref)
        return res

    @api.multi
    def Aramex_cancel_shipment(self, picking):
        return

    @api.model
    def aramex_return_send_shipping(self, sale_ids):

        self.ensure_one()
        response = []
        for sale_id in sale_ids:

            payment_option = self.aramex_payment_options
            total_value = 0.0

            total_bulk_weight = 10  # picking.weight_bulk
            list_name = []

            picking_company_id = sale_id.partner_id
            picking_partner_id = sale_id.company_id

            cCity = picking_company_id.city

            # text = "aweer wqمرحباмир"
            final_city = ""
            for t in cCity.split():
                result = regex.sub(u'[^\p{Latin}]', u'', t)
                if final_city:
                    final_city = final_city + " " + result
                else:
                    final_city = result
            picking_company_id.city = final_city

            extra_price = 0.0

            try:
                headers = {"Content-Type": "text/xml; charset=utf-8",
                           "SOAPAction": "http://ws.aramex.net/ShippingAPI/v1/Service_1_0/CreateShipments"}
                if not sale_id.picking_ids[0]:
                    raise Warning("Delivery Order not found")
                return_shipment = True
                body = self.body_request_for_aramex_send_shipping(sale_id.picking_ids[0], picking_company_id,
                                                                  picking_partner_id,
                                                                  total_value, total_bulk_weight, extra_price,
                                                                  payment_option, return_shipment)
                _logger.info("aramex Shipment Requesting Data: %s" % (body))
                url = self.get_aramex_url("/Shipping/Service_1_0.svc")
                response_body = request(method='POST', url=url, headers=headers, data=body)
                if response_body.status_code == 200:
                    api = Response(response_body)
                    results = api.dict()
                    _logger.info("aramex Shipment Response Data : %s" % (results))
                    product_details = results.get('Envelope', {}).get('Body', {}) and results.get('Envelope', {}).get(
                        'Body', {}).get('ShipmentCreationResponse', {}) or False
                    processed_shipment = product_details and product_details.get('Shipments',
                                                                                 {}) and product_details.get(
                        'Shipments', {}).get('ProcessedShipment', {}) or False
                    haserror = product_details and product_details.get('HasErrors')
                    final_tracking_no = []
                    if haserror == 'false' and processed_shipment:
                        if isinstance(processed_shipment, dict):
                            processed_shipment = [processed_shipment]
                        for detail in processed_shipment:
                            label_detail = detail.get('ShipmentLabel', {}) and detail.get('ShipmentLabel', {}).get(
                                'LabelFileContents', {})
                            tracking_no = detail.get('ID', {})
                            if detail.get('ShipmentAttachments', {}):
                                commercial_invloce = detail.get('ShipmentAttachments', {}) and detail.get(
                                    'ShipmentAttachments', {}).get('ProcessedShipmentAttachment', {}) and detail.get(
                                    'ShipmentAttachments', {}).get('ProcessedShipmentAttachment', {}).get('Url', {})
                                if commercial_invloce:
                                    pdf_converter = binascii.a2b_base64(
                                        (base64.b64encode(requests.get(commercial_invloce).content)).decode('utf-8'))
                                    mesage_obj = ("Commercial Invoice Generated ")
                                    if sale_id:
                                        sale_id.message_post(body=mesage_obj, attachments=[
                                            ('Aramex Commercial Invoice_%s.pdf' % (tracking_no), pdf_converter)])

                            form_binary_data = binascii.a2b_base64(str(label_detail))
                            label = label_detail
                            sale_id.return_label_attachment_id = self.env['ir.attachment'].create({
                                'datas': label,
                                'name': 'return_lable_{}.pdf'.format(tracking_no),
                                'datas_fname': 'return_lable_{}.pdf'.format(tracking_no)})
                            mesage_obj = (_("Shipment created!<br /> <b>Shipment Tracking Number : </b>%s") % (
                                tracking_no))
                            if sale_id:
                                sale_id.message_post(body=mesage_obj, attachments=[
                                    ('Aramex Label Form_%s.pdf' % (tracking_no), form_binary_data)])

                            final_tracking_no.append(tracking_no)
                            shipping_data = {'exact_price': extra_price, 'tracking_number': ','.join(final_tracking_no)}
                            if tracking_no:
                                sale_id.return_carrier_id = self.id
                                sale_id.return_tracking_ref = final_tracking_no[0]
                            else:
                                raise Warning("%s" % response_body.text)
                            response = [shipping_data]
                        return response
                    else:
                        raise Warning(results)
                else:
                    raise Warning(response_body.text)
            except Exception as e:
                raise Warning(e)

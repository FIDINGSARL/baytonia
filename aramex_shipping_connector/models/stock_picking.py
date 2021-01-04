import logging
import xml.etree.ElementTree as etree

from odoo.addons.aramex_shipping_connector.models.aramex_response import Response
from requests import request

from odoo import api, models
from odoo.exceptions import Warning

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def aramex_get_status(self):
        self.ensure_one()
        root_node = etree.Element("Envelope")
        root_node.attrib['xmlns'] = "http://schemas.xmlsoap.org/soap/envelope/"
        picking_company_id = self.company_id

        body = etree.SubElement(root_node, "Body")
        shipment_tracking_request = etree.SubElement(body, "ShipmentTrackingRequest")
        shipment_tracking_request.attrib['xmlns'] = "http://ws.aramex.net/ShippingAPI/v1/"

        client_info = etree.SubElement(shipment_tracking_request, "ClientInfo")
        etree.SubElement(client_info, "UserName").text = self.carrier_id.aramex_username or ''
        etree.SubElement(client_info, "Password").text = self.carrier_id.aramex_password or ''
        etree.SubElement(client_info, "Version").text = self.carrier_id.aramex_version or ''
        etree.SubElement(client_info, "AccountNumber").text = self.carrier_id.aramex_account_number or ''
        etree.SubElement(client_info, "AccountPin").text = self.carrier_id.aramex_account_pin or ''
        etree.SubElement(client_info, "AccountEntity").text = self.carrier_id.aramex_account_entity or ''
        etree.SubElement(client_info,
                         "AccountCountryCode").text = picking_company_id.country_id and picking_company_id.country_id.code or ''
        transaction = etree.SubElement(shipment_tracking_request, "Transaction")
        etree.SubElement(transaction, "Reference1").text = ""
        etree.SubElement(transaction, "Reference2").text = ""
        etree.SubElement(transaction, "Reference3").text = ""
        etree.SubElement(transaction, "Reference4").text = ""
        etree.SubElement(transaction, "Reference5").text = ""

        shipmets = etree.SubElement(shipment_tracking_request, "Shipments")
        etree.SubElement(shipmets, "string",
                         attrib={
                             "xmlns": "http://schemas.microsoft.com/2003/10/Serialization/Arrays"}).text = "%s" % self.carrier_tracking_ref
        etree.SubElement(shipment_tracking_request, "GetLastTrackingUpdateOnly").text = "true"

        body = etree.tostring(root_node).decode('utf-8')
        try:
            headers = {"Content-Type": "text/xml; charset=utf-8",
                       "SOAPAction": "http://ws.aramex.net/ShippingAPI/v1/Service_1_0/TrackShipments"}

            _logger.info("aramex Tracking Requesting Data: %s" % body)
            url = "http://ws.aramex.net/ShippingAPI.V2/Tracking/Service_1_0.svc"
            response_body = request(method='POST', url=url, headers=headers, data=body)
            if response_body.status_code == 200:
                api = Response(response_body)
                results = api.dict()
                _logger.info("Aramex Tracking Response Data : %s" % results)
                response_details = results.get("Envelope", {}).get("Body", {}).get("ShipmentTrackingResponse",
                                                                                   {})
                if response_details and response_details.get("TrackingResults", {}):
                    response_status = response_details.get("TrackingResults", {}).get(
                        "KeyValueOfstringArrayOfTrackingResultmFAkxlpY", {}).get("Value", {}).get("TrackingResult",
                                                                                                  {}).get(
                        "UpdateDescription", {})
                    _logger.info("======Aramex Status === {}".format(response_status))
                    return response_status
            else:
                raise Warning(response_body.text)
        except Exception as e:
            raise Warning(e)

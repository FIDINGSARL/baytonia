# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'EG Send to Shipper',
    'category': 'Delivery',
    'version': '11.0.1.0.0',
    'author': 'eGrivory',
    'depends': ['delivery', 'account', "stock", "eg_multiple_shipment_tracking"],
    'data': [
        "wizard/wizard_view_send_to_shipper.xml",
        "views/stock_picking.xml",
        "security/record_rule.xml"
    ],
    'application': True,
}

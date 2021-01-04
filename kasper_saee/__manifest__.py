# -*- coding: utf-8 -*-
# Part of Futurelens Studio. See LICENSE file for full copyright and licensing details.

{
    'name': 'Kasper Saee Delivery',
    'category': 'Delivery',
    'version': '11.0.1.0.0',
    'sequence': 1,
    'author': 'Futurelens Studio',
    'depends': ['delivery', 'ecom_delivery', 'eg_send_to_shipper'],
    'data': [
        'views/views.xml',
        "views/stock_picking.xml"
    ],
    'external_dependencies': {'python': ['pdfkit']},
    'application': True,
}

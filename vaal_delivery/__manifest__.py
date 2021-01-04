# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'VAAL Delivery',
    'category': 'Delivery',
    'version': '11.0.1.0.0',
    'author': 'Odoo',
    'depends': ['delivery', 'ecom_delivery', 'eg_send_to_shipper'],
    'data': [
        'views/stock_picking.xml',
        'views/views.xml',
        'data/data.xml',
        'data/cron.xml',
    ],
    'application': True,
}

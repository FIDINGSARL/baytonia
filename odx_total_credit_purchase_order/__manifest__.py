# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Credit Amount in Purchase',
    'version': '1.1',
    'category': 'Purchasing',
    'author':'Odox Softhub',
    'sequence': 35,
    'summary': 'Purchasing',
    'description': """
        Adding Total credit amount column in Purchase order
""",
    'depends': ['purchase'],
    'data': [
        'views/purchase_order_views.xml',
    ],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}

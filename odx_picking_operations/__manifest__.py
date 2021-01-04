# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Picking Operations',
    'version': '1.1',
    'category': 'Dellivery Orders',
    'author': 'Odox Soft Hub',
    'sequence': 35,
    'summary': 'Delivery Orders Report Customisation',
    'description': """
        Adding customisations for picking operations
""",
    'depends': ['stock','sale_stock'],
    'data': [
        'views/picking_operations_report.xml',

    ],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
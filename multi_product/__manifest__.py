# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Add Multiple Products',
    'version' : '1.0',
    'author':'Craftsync Technologies',
    'category': 'Sales',
    'maintainer': 'Craftsync Technologies',
    'summary': """Enable Multi Product Selection""",
    'description': """

        Multiple Product Select on single click

    """,
    'website': 'https://www.craftsync.com/',
    'license': 'OPL-1',
    'support':'info@craftsync.com',
    'depends' : ['sale_management','stock','purchase','account'],
    'data': [
        'views/product_wizard.xml',
        'views/invoice.xml',
        'views/picking.xml',
        'views/po.xml',
        'views/so.xml',
    ],
    
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['static/description/main_screen.png'],
    'price': 19.00,
    'currency': 'EUR',
}

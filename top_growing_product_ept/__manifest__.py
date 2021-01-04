# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{

    # App information
    'name': "Top Growing Products Report",
    'category': 'Sales',
    'version': '11.0',
    'summary': 'Top Growing Products report app identifies the best-selling products of your business with high growth ratio. It is calculated for a particular time period which helps to get the idea on future sales opportunities.',
    'license': 'OPL-1',

    # Dependencies
    'depends': ["eg_bigboss_toolbox"],

    # Views
    'data': [
        'security/ir.model.access.csv',
        'wizard/view_top_growing_product_report_ept.xml',
        'wizard/view_top_growing_product_report_ept_pdf.xml',
        'report/layouts.xml',
        'report/report_top_growing_product_ept.xml',

    ],

    # Odoo Store Specific
    'images': ['static/description/Top-Growing-Products-Report-Cover.jpg'],

    # Author
    "author": "Emipro Technologies Pvt. Ltd.",
    'website': 'http://www.emiprotechnologies.com/',
    'maintainer': 'Emipro Technologies Pvt. Ltd.',

    # Technical
    'installable': True,
    'auto_install': False,
    'application': True,
    'live_test_url': 'https://www.emiprotechnologies.com/free-trial?app=top-growing-product-ept&version=11&edition=enterprise',
    'price': '99',
    'currency': 'EUR',
}

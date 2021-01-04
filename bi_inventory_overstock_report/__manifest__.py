# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': "Inventory Overstock Report",
    'version': "11.0.0.0",
    'category': "Warehouse",
    'summary': "This app helps to print Inventory Overstock Product Report.",
    'description': """
    inventory over-stock report
    product overstock report
    warehouse overstock report
    overstock products report
    overstock product report
    overstock inventory report
    overstock warehouse report

    inventory over-stock product report
    inventory product overstock report
    warehouse product overstock report
    warehouse overstock products report
    inventory overstock product report
    overstock inventory product report
    overstock warehouse product report

    inventory age report
    stock age report
    stock Breakdown report
    stock Inventory Breakdown report
    Stock Inventory Age Breakdown
    Inventory stock Age Breakdown
    Inventory Breakdown Aging report
    Average age of inventory increases
    Inventory age stock report
    Inventory Age Report in Odoo & Break down report in Odoo,
    inventory to move product and increase cash flow.
    inventory dead stock report

    This app helps to print Inventory Overstock Report according to given duration of last sale and advance stock.""",
    'author': "BrowseInfo",
    'website': "www.browseinfo.in",
    'price': 49.00,
    'currency': "EUR",
    'depends': ["eg_bigboss_toolbox"],
    'data': [
        "views/inventory_overstock_wizard_view.xml",
        "report/inventory_overstock_template.xml",
        'views/inventory_overstock_line_view.xml',
        'report/inventory_overstock_line_template.xml',
    ],
    'qweb': [
    ],
    'auto_install': False,
    'installable': True,
    'live_test_url': "https://youtu.be/XaoUQy8jU6Y",
    "images": ["static/description/Banner.png"],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

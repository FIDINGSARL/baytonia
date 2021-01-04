# -*- coding: utf-8 -*-
# noinspection PyStatementEffect
{
    'name': "Baytonia Woo Commerce",

    'summary': """
        Customization on Woo Commerce for baytonia Co.
        """,

    'description': """
        Customization on Woo Commerce for baytonia Co.
        """,

    'author': "Baytonia, Eslam Yousef",
    'website': "https://oddo.baytonia.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['woo_commerce_ept','base_automation'],

    # always loaded
    'data': [
        #'data/automation_data.xml',
        'data/update_status_cron_bayt.xml',
        'views/sale_workflow_process_view.xml',
        'views/stock_location_route_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
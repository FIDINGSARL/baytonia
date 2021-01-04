{
    'name': 'Sale Order Extended',
    'category': 'sale',
    'version': '1.0',
    'author': 'eGrivory',
    'depends': ['delivery', 'ship_track', 'mass_mailing', "eg_bigboss_toolbox"],
    'data': [
        'security/access_rights.xml',
        'views/sale_order_view.xml',
        'views/res_partner_views.xml',
        'wizards/favourite_customer.xml',
        'views/issue_reason_view.xml',
        "views/issue_line_view.xml",
        "security/ir.model.access.csv",
        "wizards/issue_line_report_view.xml",
        "data/issue_line_report_cron.xml",
        "views/issue_line_screen_report.xml"
    ],
    'application': False,
}

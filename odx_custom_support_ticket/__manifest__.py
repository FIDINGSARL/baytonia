{
    'name': 'Custom Website Support',
    'version': '10.0.1.0.0',
    'author': 'Odox SoftHub',
    'website': 'http://www.odoxsofthub.com',
    'license': 'GPL-3',
    'category': 'website_support',
    'depends': ['base', 'website_support', 'eg_ticket_assign_history'
                ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/support_ticket_wizard_view.xml',
        'view/support_ticket_view.xml',
        'view/customer_satisfactory_report_view.xml',
        'wizard/support_ticket_user_wizard_view.xml',
        'report/support_ticket_report_template.xml',
        'report/support_tiket_user_report_template.xml',
        'report/report.xml',
        'view/ticket_category_path_view.xml'

    ],
    'installable': True,
    'auto_install': False,
}

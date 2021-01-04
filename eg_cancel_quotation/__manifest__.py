{
    'name': 'EG Cancel and Confirm Quotations',
    'version': '11.0',
    'summery': 'Cancel and Confirm all selected  quotations at once.',
    'author': 'eGrivory || DC',
    'depends': ['sale_management'],
    'data': [
        'security/group.xml',
        'views/sale_order_wizard.xml',
    ],
    'application': True,
    'installable': True,
    'autoinstall': False,
}

{
    'name': 'Scrap Order Report ',
    'version': '10.0.1.0.0',
    'author': 'Odox SoftHub',
    'website': 'http://www.odoxsofthub.com',
    'license': 'GPL-3',
    'category': 'Stock',
    'depends': ['base', 'stock','delivery'
                ],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_scrap_view.xml',
        'report/scrap_order_template.xml',
        'report/report.xml',
        'wizard/scrap_report_wizard_view.xml',
        'views/attachment_view.xml'

    ],
    'installable': True,
    'auto_install': False,
}

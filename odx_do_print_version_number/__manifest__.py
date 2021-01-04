{
    'name': 'DO Print Version Number',
    'version': '10.0.1.0.0',
    'author': 'Odox SoftHub',
    'website': 'http://www.odoxsofthub.com',
    'license': 'GPL-3',
    'category': 'Stock',
    'depends': ['base','stock','sale_stock_extended','eg_do_user_assignment',
                'odx_picking_operation_report','purchase'
                ],
    'data': [

        'view/picking_view.xml',
        'view/purchase_view.xml',
        'report/report_picking_template.xml',
        'report/purchase_report_template.xml'

    ],
    'installable': True,
    'auto_install': False,
}

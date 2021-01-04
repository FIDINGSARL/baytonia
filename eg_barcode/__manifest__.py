{
    'name': 'Barcode',
    'version': '11.0.0.0.0',
    'summery': 'eG Barcode',
    "author": "eGrivory || DC",
    'depends': ['eg_odoo_magento_connect_extended'],
    "data": [
        'security/ir.model.access.csv',
        'views/eg_picking_barcode_report_views.xml',
        'views/eg_picking_barcode_view.xml',
        'views/eg_picking_barcode_configuration.xml',
        'views/eg_report_deliveryslip.xml',
        'views/eg_report_stockpicking_operations.xml',
        'views/open_barcode_view.xml',
        'views/product_product_view.xml',
        'views/eg_picking_barcode_line_view.xml',
    ],
    'application': True,
    'installable': True,
    'autoinstall': False,

}

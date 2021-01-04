{
    'name': 'Do Barcode Custom Delivery Method',
    'version': '10.0.1.0.0',
    'author': 'Odox SoftHub',
    'website': 'http://www.odoxsofthub.com',
    'license': 'GPL-3',
    'category': 'delivery',
    'depends': ['base','eg_custom_delivery','eg_odoo_magento_connect_extended',
                'delivery','ship_track','eg_send_to_shipper'
                ],
    'data': [

        'views/delivery_cariier_view.xml',
        'report/delivery_report.xml',
        'views/picking_view.xml',
        'wizard/wizard_send_to_shipper_view.xml'

    ],
    'installable': True,
    'auto_install': False,
}

{
    'name': 'Customer review',
    'version': '10.0.1.0.0',
    'author': 'Odox SoftHub',
    'website': 'http://www.odoxsofthub.com',
    'license': 'GPL-3',
    'category': 'stock',
    'depends': ['base','sale','eg_unifonic_sms','stock','eg_multiple_shipment_tracking',
                'aramex_shipping_connector','smsa_delivery','vaal_delivery','eg_clex_delivery'
                ],
    'data': [
        'data/data.xml',
        'data/delivery_status_update_crone.xml',
        'views/stock_picking_view.xml',
        'data/send_sms_crone.xml',

    ],
    'installable': True,
    'auto_install': False,
}

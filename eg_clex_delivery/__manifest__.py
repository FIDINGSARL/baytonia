{
    'name': 'CLEX Delivery Integration eG',
    'version': '11.0',
    'category': 'shipping',
    'depends': ['eg_send_to_shipper'],
    'license': 'OPL-1',
    "author": "eGrivory || DC",
    'data': [
        'views/delivery_carrier.xml',
        'views/sale_order_view.xml',

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

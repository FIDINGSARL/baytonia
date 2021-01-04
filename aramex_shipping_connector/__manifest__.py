{
    # App information
    'name': 'Aramex Shipping ',
    'category': 'Website',
    'version': '11.0',
    'license': 'OPL-1',

    # Dependencies
    'depends': ['delivery', 'eg_send_to_shipper'],

    # views
    'data': ['views/aramex_delivery_carrier_view.xml',
             'views/sale_order_view.xml'
             # 'data/data.xml',
             ],

    # Technical
    'installable': True,
    'application': True,
    'auto_install': False,

}

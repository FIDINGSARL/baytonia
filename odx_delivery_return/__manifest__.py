{
    'name': 'Delivery Return',
    'version': '10.0.1.0.0',
    'author': 'Odox SoftHub',
    'website': 'http://www.odoxsofthub.com',
    'license': 'GPL-3',
    'category': 'Stock',
    'depends': ['base','sale','stock','account','eg_send_to_shipper','eg_odoo_magento_connect_extended'
                ],
    'data': [
        'security/security.xml',
        'views/invoice_view.xml',
        'views/stock_view.xml'

    ],
    'installable': True,
    'auto_install': False,
}

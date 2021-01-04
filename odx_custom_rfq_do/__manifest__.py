{
    'name': 'Custom DO ',
    'version': '10.0.1.0.0',
    'author': 'Odox SoftHub',
    'website': 'http://www.odoxsofthub.com',
    'license': 'GPL-3',
    'category': 'Stock',
    'depends': ['base', 'sale', 'stock', 'account','sale_timing','ship_track','eg_odoo_magento_connect_extended'
                ],
    'data': [
        'view/delivery_view.xml',
        # 'data/mail_template.xml'

    ],
    'installable': True,
    'auto_install': False,
}

{
    'name': 'sale order and delivery confirm ',
    'version': '10.0.1.0.0',
    'author': 'Odox SoftHub',
    'website': 'http://www.odoxsofthub.com',
    'license': 'GPL-3',
    'category': 'Sale',
    'depends': ['base', 'sale', 'stock', 'account', 'stock_account', 'sale_management',
                'eg_odoo_magento_connect_extended', 'eg_send_to_shipper'
                ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/data.xml',
        'view/sale_view.xml',
        'view/sale_auto_config_view.xml',
        'view/piking_view.xml'

    ],
    'installable': True,
    'auto_install': False,
}

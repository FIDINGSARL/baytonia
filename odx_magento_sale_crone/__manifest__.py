{
    'name': 'Magento Sale order crone',
    'version': '10.0.1.0.0',
    'author': 'Odox SoftHub',
    'website': 'http://www.odoxsofthub.com',
    'license': 'GPL-3',
    'category': 'Sale',
    'depends': ['base','product','odoo_magento_connect','sale',
                'eg_odoo_magento_connect_extended'
                ],
    'data': [

        'data/sale_status_crone.xml',

    ],
    'installable': True,
    'auto_install': False,
}

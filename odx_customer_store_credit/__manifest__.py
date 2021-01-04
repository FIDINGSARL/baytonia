{
    'name': 'Customer Store Credit',
    'version': '10.0.1.0.0',
    'author': 'Odox SoftHub',
    'website': 'http://www.odoxsofthub.com',
    'license': 'GPL-3',
    'depends': ['base', 'account', 'sale', 'bridge_skeleton', 'odoo_magento_connect',
                'eg_odoo_magento_connect_extended', 'eg_unifonic_sms'
                ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'view/sms_instance_view.xml',
        'view/partner_view.xml',
        'view/sale_view.xml',
        # 'view/product_view.xml',
        'view/account_view.xml'

    ],
    'installable': True,
    'auto_install': False,
}

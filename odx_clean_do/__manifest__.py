{
    'name': 'Clean DO',
    'version': '10.0.1.0.0',
    'author': 'Odox SoftHub',
    'website': 'http://www.odoxsofthub.com',
    'license': 'GPL-3',
    'depends': ['base', 'stock', 'eg_odoo_magento_connect_extended', 'kasper_saee', 'smsa_delivery',
                'vaal_delivery', 'odoo_consignment_process', 'eg_vendor_in_do', 'odoo_magento_connect',
                'sale_timing'

                ],
    'data': [

        'view/stock_picking.xml'

    ],
    'installable': True,
    'auto_install': False,
}

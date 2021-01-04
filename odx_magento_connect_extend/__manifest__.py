{
    'name': 'Magento Connect Extend',
    'version': '10.0.1.0.0',
    'author': 'Odox SoftHub',
    'website': 'http://www.odoxsofthub.com',
    'license': 'GPL-3',
    'category': 'Stock',
    'depends': ['base','product','odoo_magento_connect', 'eg_send_to_shipper', 'auto_invoice_workflow_ept',
                'eg_odoo_magento_connect_extended','account','sale_stock','bridge_skeleton'
                ],
    'data': [
        'data/update_magento_product_type.xml',
        'view/product_product_view.xml',
        'view/product_view.xml',
        'view/sale_view.xml',

    ],
    'installable': True,
    'auto_install': False,
}

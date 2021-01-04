{
    'name': 'Sale Order Ticket',
    'version': '0.1',
    'author': 'eGrivory',
    'website': 'https://www.eGrivory.com',
    'category': 'Website',
    'summary': 'Ticket Created from Sale Order',
    'depends': ['website_support', 'eg_vendor_in_do', 'eg_odoo_magento_connect_extended'],
    'data': [
        'views/sale_order_view.xml',
        'views/customer_support_view.xml',
        'views/stock_picking_view.xml',
    ],
    'installable': True,
}

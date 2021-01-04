{
    'name': 'Sale Stock Extended',
    'category': 'sale',
    'version': '1.0',
    'author': 'eGrivory',
    'depends': ['sale_stock'],
    'data': [
        'views/sale_order_view.xml',
        'views/stock_picking.xml',
        "views/product_product_view.xml",
        "wizards/cancel_warning_wizard_view.xml",
        "security/record_rule.xml",
    ],
    'application': False,
}

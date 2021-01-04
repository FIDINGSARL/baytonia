{
    'name': 'Import Inventory Adjustment',
    'version': '11.0',
    'summary': 'Import Inventory Adjustment',
    'description': """
    """,
    'author': 'eGrivory',
    'depends': ["stock"],
    'data': [
        'data/ir_sequence_data.xml',
        'views/import_stock_inventory_view.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}

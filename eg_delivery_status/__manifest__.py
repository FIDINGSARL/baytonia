{
    'name': 'eG Stock Picking Status',
    'version': '11.0',
    'summery': 'EG Delivery',
    "author": "eGrivory || DC",
    'depends': ['sale', 'sale_stock', 'account'],
    "data": [
        'security/ir.model.access.csv',
        'views/stock_picking_status.xml',
        'views/stock_picking.xml',
    ],
    'application': True,
    'installable': True,
    'autoinstall': False,

}

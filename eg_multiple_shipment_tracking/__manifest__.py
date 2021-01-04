{
    'name': 'Multiple Shipment Tracking eG',
    'version': '11.0',
    'category': 'shipping',
    'depends': ['sale_stock', 'purchase', 'delivery'],
    'license': 'OPL-1',
    "author": "eGrivory || DC",
    'data': [
        'views/stock_picking_views.xml',
        'views/delivery_tracking_line.xml',
        'security/ir.model.access.csv',
        'data/service_cron_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

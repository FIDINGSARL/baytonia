{
    "name": "Consignment Extended",
    "summary": "To restrict consignment order in PO/SO view",
    "version": "1.1.0",
    "sequence": 1,
    "author": "eGrivory || DC",
    "depends": ['purchase', 'sale'],
    "data": [
        'views/purchase_order.xml',
        'views/sale_order_view.xml',
    ],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}

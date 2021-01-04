{
    "name": "Delivery User Validation",
    "summary": "Restrict user to validate Incoming shipment or delivery order",
    "version": "1.1.0",
    "sequence": 1,
    "author": "eGrivory || DC",
    "depends": ['delivery'],
    "data": [
        'wizards/approve_stock_picking_wizard.xml',
        'security/group.xml'
        # 'views/product_product_view.xml'

    ],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}

{
    "name": "Vendor Code",
    "summary": "Module for adding vendor code field and search based on vendor code",
    "version": "1.1.0",
    "sequence": 1,
    "author": "eGrivory || DC",
    "depends": ['purchase', 'stock', 'product'],
    "data": [
        'views/res_partner_views.xml',
        "wizards/set_vendor_product_view.xml"
    ],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}

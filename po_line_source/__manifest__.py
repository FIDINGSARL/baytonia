{
    'name': "PO Line Source",

    'summary': "Purchase order line source",

    'description': """
         Purchase order line source if its coming automatically.
    """,

    'author': "MNP",
    'website': "MNP",

    'category': 'Test',
    'version': '0.1',

    'depends': ['sale_stock'],

    'data': [
        'view/purchase_view.xml',
        'view/account_invoice_view.xml',
        'view/stock_picking.xml'
    ],

}

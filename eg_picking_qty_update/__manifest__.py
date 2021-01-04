{
    'name': 'Picking Update done Quantity',
    'version': '0.1',
    'category': 'Sale Stock',
    'description': """
        - This App extra Functionality of delivery order Created.
        - Open pop-up and Set quantity done.
    """,
    'depends': ['stock'],
    'data': [

        'wizards/qty_update_wizard.xml',

        'views/stock_picking_view.xml',
    ],
    'installable': True,

}

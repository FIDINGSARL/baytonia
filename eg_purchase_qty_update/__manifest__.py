{
    'name': 'Purchase Order Update Quantity and Price',

    'version': '0.1',

    "author": "eGrivory",

    "website": "http://www.egrivory.com",

    'category': 'Purchase Order',

    'description': """
        - This App extra Functionality of Purchase order Created.
        - Open pop-up and Set quantity and price.
    """,

    'depends': ['purchase'],

    'data': [

        'wizards/qty_update_wizard.xml',

        'views/purchase_order_view.xml',
    ],

    'installable': True,

}

{
    'name': "Ship Track",

    'summary': "tracking shipment",

    'description': """
         Ship track module for tracking order delivery.
    """,

    'author': "MNP",
    'website': "MNP",

    'category': 'Test',
    'version': '0.1',

    'depends': ['sale_stock', 'product', 'delivery', 'vaal_delivery', 'smsa_delivery',
                'kasper_saee'],

    'data': [

        'view/stock_picking.xml',
        'view/sale_order.xml',
        'view/product_template_view.xml',
        'view/account_invoice.xml',
        'view/product_product_view.xml',
        'view/purchase_view.xml',
        'report/report_invoice.xml',
        'data/cron.xml'

    ],

}

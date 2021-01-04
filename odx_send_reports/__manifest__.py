{
    'name': 'Send Reports',
    'version': '10.0.1.0.0',
    'author': 'Odox SoftHub',
    'website': 'http://www.odoxsofthub.com',
    'license': 'GPL-3',
    'depends': ['base', 'eg_bigboss_toolbox', 'mail', 'non_moving_product_ept', 'eg_hero_product_report',
                'eg_product_percent_sale_report','product','sale'
                ],
    'data': [

        'data/send_reports.xml',
        'data/email_template.xml',
         'report/report.xml',
        'report/ordered_qty.xml',
        'report/invoiced_qty.xml',
        'report/delivered_qty.xml',
        'report/stock_product.xml',
        'report/mto_product.xml',
        'report/non_moving_product.xml'


    ],
    'installable': True,
    'auto_install': False,
}

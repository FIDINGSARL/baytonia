{
    'name': 'Vendor Lead Time ',
    'version': '10.0.1.0.0',
    'author': 'Odox SoftHub',
    'website': 'http://www.odoxsofthub.com',
    'license': 'GPL-3',
    'category': 'Customer',
    'depends': ['base','stock','product'
                ],
    'data': [
        'views/partner_view.xml',
        'views/product_product_view.xml'
        # 'view/mail_template_view.xml'

    ],
    'installable': True,
    'auto_install': False,
}

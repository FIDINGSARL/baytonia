{
    'name': 'Byt Sale Credit Limit',
    'version': '1.0',
    'sequence': 1,
    'summary': 'Credit Status on Sale',
    'description': """
        Credit Status

    """,
    'author': 'MNP',
    'sequence': 1,
    'depends': ['sale', 'account'],
    'data': [
        'views/sale_view.xml'

    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'bootstrap': True

}

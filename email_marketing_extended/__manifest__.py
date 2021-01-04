{
    # App information
    'name': 'Email Marketing Extended',
    'category': 'Marketing',
    'version': '1.0',
    "author": "eGrivory || DC",
    'license': 'OPL-1',

    # Dependencies
    'depends': ['mass_mailing'],

    # views
    'data': [
        'data/cron.xml',
        'views/mass_mailing_views.xml',
        'wizards/add_contacts_to_list.xml'
    ],

    # Technical
    'installable': True,
    'application': False,
    'auto_install': False,

}

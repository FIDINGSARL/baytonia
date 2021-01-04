{
    'name': 'Auto Sms And Email',
    'version': '10.0.1.0.0',
    'author': 'Odox SoftHub',
    'website': 'http://www.odoxsofthub.com',
    'license': 'GPL-3',
    'category': 'Sale',
    'depends': ['base','sale','eg_unifonic_sms','mail'
                ],
    'data': [
        # 'data/auto_msg_email.xml',
        'wizard/wizard_view.xml',
        'data/mail_template.xml',
        'view/sale_view.xml'

    ],
    'installable': True,
    'auto_install': False,
}

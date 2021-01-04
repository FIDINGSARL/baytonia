{
    'name': 'Eg Unifonic Website Support',

    'version': "11.0",

    'category': "Customer Support",

    'summary': "Post SMS",

    'author': "eGrivory",

    'depends': ["eg_unifonic_sms", "website_support", "eg_ticket_from_so_do"],

    'data': ["views/sms_instance_view.xml"],
    'installable': True,
    'application': True,
    'auto_install': False,
}

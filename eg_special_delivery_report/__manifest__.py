{
    'name': 'Special Delivery Report',

    'version': "11.0",

    'category': "Delivery Report",

    'summary': "Report of delivery order when order state is ready and delivery method is custom delivery",

    'author': "eGrivory",

    'depends': ["stock", "eg_delivery_status"],

    'data': ["wizards/special_delivery_report_view.xml"],
    'installable': True,
    'application': True,
    'auto_install': False,
}

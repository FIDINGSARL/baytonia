{
    'name': 'Eg FreshChat Msg',

    'summary': "Post Whatsapp Message",

    'author': "eGrivory",

    'website': "http://www.eGrivory.com",

    'type': "Information",

    'version': "1.1.1",

    'depends': ["eg_msg_base", "sale"],

    'data': ["views/sms_instance_view.xml",
             "views/freshchat_template_view.xml",
             "wizards/post_sms_wizard_view.xml",
             "views/sale_order_view.xml",
             "security/ir.model.access.csv",
             "views/msg_delivery_report_view.xml"]
}

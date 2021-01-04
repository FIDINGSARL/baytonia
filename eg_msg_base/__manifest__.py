# sudo pip3 install git+https://github.com/ClickSend/clicksend-python
{
    'name': 'Eg Msg Base',

    'version': "11.0",

    'category': "sales",

    'summary': "Post Sms",

    'author': "eGrivory",

    'depends': ["base"],

    'data': [
        "views/calling_code_view.xml",
        "data/auto_calling_code_view.xml",
        "views/msg_status_view.xml",
        "views/sms_instance_view.xml",
        "views/msg_delivery_report_view.xml",
        "views/msg_error_log_view.xml",
        "wizard/post_sms_wizard_view.xml",
        "views/number_list_view.xml",
        "wizard/add_multi_number_wizard_view.xml",
        "views/group_msg_view.xml",
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/msg_delivery_report_cron.xml",
        "views/sms_template_view.xml"],
    'installable': True,
    'application': True,
    'auto_install': False,
}

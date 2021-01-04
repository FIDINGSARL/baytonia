{
    'name': 'Eg Unifonic Sms',

    'summary': "Post Sms",

    'author': "eGrivory",

    'website': "http://www.eGrivory.com",

    'type': "Information",

    'version': "1.1.1",

    'depends': ["eg_msg_base", "eg_odoo_magento_connect_extended"],

    'data': ["wizards/unifonic_post_sms_wizard_view.xml",
             "views/sms_instance_view.xml",
             "views/msg_sender_view.xml",
             "data/check_balance_cron.xml",
             "views/msg_records_view.xml",
             "data/send_msg_record_cron.xml",
             "data/send_failed_msg_record_cron.xml",
             "data/change_state_msg_record_cron.xml",
             "views/msg_error_log_view.xml",
             "views/sale_order_view.xml",
             "security/ir.model.access.csv",
             "views/msg_delivery_report_view.xml"]
}

{
    'name': 'Eg Sale Order Report',

    'summary': "Given report for particular date",

    'author': "eGrivory",

    'website': "http://www.eGrivory.com",

    'type': "Information",

    'version': "0.0.1",

    'depends': ["eg_bigboss_toolbox"],

    'data': [
        "wizard/sale_order_report_wizard_view.xml",
        "data/picking_barcode_report_daily_cron.xml"
    ]
}

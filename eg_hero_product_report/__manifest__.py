{
    "name": "Hero Product Report",

    "summary": "Generate Report for if product quantity on hand and Generate Report for if product Make to Order",

    "category": "Report",

    "version": "1.0.1",

    "author": "eGrivory",

    "website": "http://www.egrivory.com",

    "depends": ["eg_bigboss_toolbox",'odx_vendor_lead_time'],

    "data": ["wizards/hp_stock_report_view.xml",
             "wizards/hp_mto_report_view.xml",
             "wizards/hp_mto_line_report_view.xml",
             "wizards/hp_stock_line_report_view.xml",
             "reports/hp_stock_line_report_template.xml",
             "reports/hp_mto_line_report_template.xml",
             "data/hp_stock_report_cron.xml",
             ]
}

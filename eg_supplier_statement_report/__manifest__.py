{
    "name": "Supplier Statement Report",
    "summary": "Module for Supplier Statement regarding SO and PO.",
    "version": "1.1.0",
    "sequence": 1,
    "author": "eGrivory || DC",
    "depends": ["eg_bigboss_toolbox",'odx_vendor_lead_time'],
    "data": [
        'wizards/supplier_statement_report_view.xml',
        'data/schedule_action_view.xml',
        'views/supplier_statement_report_line_view.xml'
    ],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}

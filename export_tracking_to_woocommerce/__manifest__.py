{
    "name": "Export Tracking to Woocommerce",
    "summary": "Module for sending tracking details to Woocommerce",
    "version": "1.1.0",
    "sequence": 1,
    "author": "eGrivory || DC",
    "depends": ['sale'],
    "data": [
        'views/sale_order_view.xml',
        'data/cron.xml',
        'data/update_customer_email_template.xml'
    ],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}

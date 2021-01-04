{
    'name': 'Delivery Order Slip',
    'version': '0.1',
    'description': 'Delivery Order Extended',
    'author': 'eGrivory',
    'website': 'www.egrivory.com',
    'category': 'Stock',
    'depends': ['delivery','delivery_company_report_eg'],
    'data': [
        'reports/delivery_slip_report_extended.xml',
        'data/custome_delivery_tracking_number.xml'
    ],
    'installable': True,
}

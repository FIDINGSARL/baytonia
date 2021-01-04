{
    'name': 'Delivery Order Ticket',
    'version': '0.1',
    'author': 'eGrivory',
    'website': 'https://www.eGrivory.com',
    'category': 'Website',
    'summary': 'Ticket Created from Delivery Order',
    'depends': ['stock', 'website_support'],
    'data': [
        'views/stock_picking_view.xml',
        'views/website_support_ticket_view.xml',
    ],
    'installable': True,

}

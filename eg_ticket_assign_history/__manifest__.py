{
    'name': 'Ticket Assign History',
    'version': '0.1',
    'author': 'eGrivory',
    'website': 'https://www.eGrivory.com',
    'category': 'Website',
    'summary': 'History of Tickets ',
    'depends': ['website_support'],
    'data': [
        'views/ticket_assign_history_view.xml',
        'views/website_support_ticket_view.xml',

        'security/ir.model.access.csv',
    ],
    'installable': True,

}

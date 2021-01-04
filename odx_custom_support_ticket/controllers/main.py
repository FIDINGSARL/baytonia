# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class cutomerSupportTicket(http.Controller):

    @http.route('/create/support_ticket', type='json', auth='user', methods=['PUT'], csrf=False)
    def create_support_ticket(self, **kwargs):
        subject = kwargs.get('subject')
        name = kwargs.get('name')
        order_number = kwargs.get('order_number')
        email = kwargs.get('email')
        description = kwargs.get('description')
        categories_id = int(kwargs.get('category'))

        sale_order = request.env['sale.order'].sudo().search(
            [('name', '=', order_number)], limit=1)
        category = request.env['website.support.ticket.categories'].sudo().search(
            [('id', '=', categories_id)], limit=1)

        support_ticket = request.env['website.support.ticket'].sudo().create({
            'subject': subject,
            'person_name': name,
            'sale_order_id': sale_order.id if sale_order else False,
            'email': email,
            'category': category.id if category else False,
            'description': description
        })

        if support_ticket:
            result = {
                'message': "Sucessfully Created Ticket",
            }
        else:
            result = {
                'message': "Cannot Create Ticket",
            }
        return result

    @http.route('/support_ticket/categories', type='json', auth='user', methods=['GET'], csrf=False)
    def support_ticket_categories(self, **kwargs):
        category_access = []
        for category_permission in http.request.env.user.groups_id:
            category_access.append(category_permission.id)

        ticket_categories = http.request.env['website.support.ticket.categories'].sudo().search_read(
            ['|', ('access_group_ids', 'in', category_access), ('access_group_ids', '=', False),
             ('is_active', '=', True)], ['name'])

        if ticket_categories:
            result = {
                'categories': ticket_categories
            }
        else:
            result = {
                'message': "Cannot Find categories ",
            }
        return result

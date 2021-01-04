from odoo import models, fields, api


class TicketCategoryPath(models.Model):
    _name = 'ticket.category.path'
    _rec_name = 'category_id'

    category_id = fields.Many2one('website.support.ticket.categories', string="Category",required=1)
    user_state_ids = fields.One2many('user.state','ticket_category_path_id','User State')

    _sql_constraints = [
        ('category_id_uniq', 'unique (category_id)', "Category should be Unique !"),
    ]


class UserState(models.Model):
    _name = 'user.state'

    stage = fields.Integer('Stage')
    state = fields.Many2one('website.support.ticket.states',string="State")
    ticket_category_path_id = fields.Many2one('ticket.category.path','Ticket Category Path')
    user_id = fields.Many2one('res.users', string="Assigned User")


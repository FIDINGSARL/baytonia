from odoo import models, fields, api


class SmsInstance(models.Model):
    _inherit = "sms.instance"

    user_assign_msg = fields.Text(string="User Assign",
                                  help="This is for Customer Support and {{person_name}} == Person Name, "
                                       "{{ticket_number}} == Ticket Number")

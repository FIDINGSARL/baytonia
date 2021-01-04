from odoo import models, fields, api


class SurveyQuestion(models.Model):
    _inherit = 'survey.question'

    type = fields.Selection(selection_add=[('order', 'Order Number'), ('ticket', 'Ticket Number')])
    customer_support_survey = fields.Boolean(string="Customer Support Survey")


class SurveyUserInputLine(models.Model):
    _inherit = 'survey.user_input_line'

    answer_type = fields.Selection(selection_add=[('order', 'Order Number'), ('ticket', 'Ticket Number')])
    order = fields.Text("order")
    ticket = fields.Text("Ticket")

    @api.model
    def save_line_order(self, user_input_id, question, post, answer_tag):
        vals = {
            'user_input_id': user_input_id,
            'question_id': question.id,
            'survey_id': question.survey_id.id,
            'skipped': False,
        }
        if answer_tag in post and post[answer_tag].strip():
            vals.update({'answer_type': 'order', 'order': post[answer_tag]})
        else:
            vals.update({'answer_type': None, 'skipped': True})
        old_uil = self.search([
            ('user_input_id', '=', user_input_id),
            ('survey_id', '=', question.survey_id.id),
            ('question_id', '=', question.id)
        ])
        if old_uil:
            old_uil.write(vals)
        else:
            old_uil.create(vals)
        return True

    @api.model
    def save_line_ticket(self, user_input_id, question, post, answer_tag):
        vals = {
            'user_input_id': user_input_id,
            'question_id': question.id,
            'survey_id': question.survey_id.id,
            'skipped': False,
        }
        if answer_tag in post and post[answer_tag].strip():
            vals.update({'answer_type': 'ticket', 'ticket': post[answer_tag]})
        else:
            vals.update({'answer_type': None, 'skipped': True})
        old_uil = self.search([
            ('user_input_id', '=', user_input_id),
            ('survey_id', '=', question.survey_id.id),
            ('question_id', '=', question.id)
        ])
        if old_uil:
            old_uil.write(vals)
        else:
            old_uil.create(vals)
        return True


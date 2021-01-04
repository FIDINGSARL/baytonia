from odoo import api, models



class SupportTicketReportUser(models.AbstractModel):
    _name = 'report.odx_custom_support_ticket.support_tikcet_template'

    @api.multi
    def get_report_values(self, docids, data=None):
        wiz = self.env['support.ticket.report.wiz'].browse(data.get('wiz_id'))
        date_to = str(wiz.date_to) + ' ' + '23:59:59'
        date_from = str(wiz.date_from) + ' ' + '00:00:00'
        domain = []
        if wiz.date_to and wiz.date_from:
            domain.append(('create_date', '<=', date_to))
            domain.append(('create_date', '>=', date_from))
        if wiz.category:
            domain.append(('category', 'in', wiz.category.ids))
        if wiz.user:
            domain.append(('user_id', 'in', wiz.user.ids))
        tickets = self.env['website.support.ticket'].search(domain)

        return {
            'tickets': tickets,
            'date_to': wiz.date_to,
            'date_from': wiz.date_from,
        }


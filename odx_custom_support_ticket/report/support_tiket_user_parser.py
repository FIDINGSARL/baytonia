from odoo import api, models


class SupportTicketReport(models.AbstractModel):
    _name = 'report.odx_custom_support_ticket.support_tikcet_user_template'

    @api.multi
    def get_report_values(self, docids, data=None):
        wiz = self.env['support.user.report.wiz'].browse(data.get('wiz_id'))
        date_to = str(wiz.date_to) + ' ' + '23:59:59'
        date_from = str(wiz.date_from) + ' ' + '00:00:00'
        domain = []
        domain_user = []
        if wiz.date_to and wiz.date_from:
            domain.append(('create_date', '<=', date_to))
            domain.append(('create_date', '>=', date_from))
        if wiz.category:
            domain.append(('category', 'in', wiz.category.ids))
        if wiz.user:
            domain.append(('user_id', 'in', wiz.user.ids))
            domain_user.append(('id', 'in', wiz.user.ids))
        tickets = self.env['website.support.ticket'].search(domain)
        users = self.env['res.users'].search(domain_user)
        result = []
        for user in users:
            created_count = 0
            assigned_count =0
            closed_count = 0
            duration =0
            hours = 0
            minutes = 0
            res = dict(
                (fn, 0.0) for fn in
                ['user', 'created', 'assigned','closed', 'duration','hours','minutes'])
            for ticket in tickets:
                if ticket.create_uid == user:
                    created_count +=1
                for assigned in ticket.ticket_assign_history_ids:
                    if assigned.user_id == user:
                        assigned_count +=1
                        duration += assigned.days
                        hours += assigned.hours
                        minutes += assigned.minutes
                        if minutes >= 60:
                            extra_hours = int(minutes/60)
                            hours += extra_hours
                            minutes -=(extra_hours*60)
                        if hours >= 24:
                            extra_day = int(hours/24)
                            duration += extra_day
                            hours -= (extra_day * 24)
                        if assigned.end_date:
                            closed_count +=1
            res['user']  = user.name
            res['created'] = created_count
            res['assigned'] = assigned_count
            res['closed'] = closed_count
            res['duration'] = round(duration / closed_count,2) if closed_count !=0 else 0
            res['hours'] = round(hours / closed_count, 2) if closed_count != 0 else 0
            res['minutes'] = round(minutes / closed_count, 2) if closed_count != 0 else 0
            result.append(res)
        return {
            'result': result,
            'date_to': wiz.date_to,
            'date_from': wiz.date_from,
        }

# create_uid

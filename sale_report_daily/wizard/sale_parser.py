import base64

from odoo import models,api
from datetime import datetime,date,timedelta



class SaleParser(models.AbstractModel):
    _name = 'report.sale_report_daily.report_action_to_template'

    @api.model
    def get_report_values(self,docids,data=None):

        sale = self.env['sale.order'].search([])
        sale_list = []
        quotation_list =[]
        report_name= ''
        report_date=''

        for rec in sale:
           if rec.date_order:
                datet1 = datetime.strptime(rec.date_order, '%Y-%m-%d %H:%M:%S').date()
                if data.get('dat') == 'daily':
                    report_name = 'Daily Sale Report'
                    report_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    if datet1 == date.today():
                            d = {
                                'order': rec.name,
                                'date':rec.confirmation_date,
                                'customer':rec.partner_id.name,
                                'salesperson':rec.user_id.name,
                                'total':rec.amount_total,
                                'status':rec.state,
                                'waiting_time':rec.waiting_time,
                                'waiting_time_delivery':rec.waiting_time_delivery


                            }
                            if rec.state in ['draft','sent']:
                                quotation_list.append(d)
                            elif rec.state in ['sale','done']:
                                sale_list.append(d)

                elif data['dat'] == 'monthly':
                    if datet1.month == date.today().month:
                        report_name = 'Monthly Sale Report'
                        report_date =datet1.strftime("%B")
                        d = {
                            'order': rec.name,
                            'date': rec.confirmation_date,
                            'customer': rec.partner_id.name,
                            'salesperson': rec.user_id.name,
                            'total': rec.amount_total,
                            'status': rec.state,
                            'waiting_time': rec.waiting_time,
                            'waiting_time_delivery': rec.waiting_time_delivery
                        }
                        if rec.state in ['draft','sent']:
                            quotation_list.append(d)
                        elif rec.state in ['sale','done']:
                                sale_list.append(d)
                else:
                    if datet1.year== date.today().year:
                        report_name = 'Yearly Sale Report'
                        report_date =date.today().year
                        d = {
                            'order': rec.name,
                            'date': rec.confirmation_date,
                            'customer': rec.partner_id.name,
                            'salesperson': rec.user_id.name,
                            'total': rec.amount_total,
                            'status': rec.state,
                            'waiting_time': rec.waiting_time,
                            'waiting_time_delivery': rec.waiting_time_delivery
                        }
                        if rec.state in ['draft','sent']:
                            quotation_list.append(d)
                        elif rec.state in ['sale','done']:
                                sale_list.append(d)


        return {
            'list_of_sale_order' : sale_list,
            'list_of_qoutation':quotation_list,
            'report_name':report_name,
            'report_date':report_date
             }
    #
    # @api.model
    # def get_repor(self,data):
    #
    #     att_id = self.env['ir.attachment'].create({
    #
    #         'name': 'My name',
    #
    #         'type': 'binary',
    #
    #         'datas': base64.encodestring(data),
    #
    #         'datas_fname': 'Myname.pdf',
    #
    #         'res_model': 'account.invoice',
    #
    #         'res_id': invoice.id,
    #
    #         'mimetype': 'application/x-pdf'
    #
    #     })



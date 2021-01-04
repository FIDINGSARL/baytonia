import json
from datetime import date

import requests

from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    add_substract = fields.Float("Add or substract a credit value")
    store_credit = fields.Float("Store Credit", readonly=1, store=True)
    payment_odoo_history = fields.One2many('store.credit.history', 'partner_id', "Store Credit History", readonly=1)

    @api.multi
    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        ctx = dict(self._context or {})
        connectionObj = self.env['magento.configure'].search([('active', '=', True)])
        ctx['instance_id'] = connectionObj.id
        if vals.get('add_substract'):
            for rec in self:
                amount = 0
                amount = rec.store_credit + rec.add_substract
                if amount > 0:
                    amount = amount
                else:
                    amount = 0
                ticket_user_line_obj = self.env['store.credit.history']
                ticket_user_line_obj.create({
                    'balance_change': rec.add_substract,
                    'new_balance': amount,
                    'partner_id': rec.id,
                    'user_id': self.env.user.id,
                })
                rec.store_credit = amount
                if connectionObj.active:
                    if connectionObj.state != 'enable':
                        return False
                connection = self.env['magento.configure'].with_context(ctx)._create_connection()
                if connection:
                    url = connection[0]
                    token = connection[1]
                    customer_mapping_id = self.env["magento.customers"].search([('oe_customer_id', '=', rec.id)])
                    if customer_mapping_id:
                        customer_id = customer_mapping_id.mag_customer_id
                        current_date = date.today()
                        addr = rec.address_get(['delivery', 'invoice'])
                        to_number = ''
                        if addr:
                            contact = self.browse([addr['invoice']])
                            to_number = contact.phone
                        else:
                            to_number = rec.phone
                        sms_instance_id = self.env["sms.instance"].search([("provider", "=", "unifonic_sms")],limit=1)
                        message =''
                        if sms_instance_id:
                            message = sms_instance_id.store_credit_message
                            if message:
                                message = message.replace("{{name}}", rec.name)
                                message = message.replace("{{credit}}", str(rec.add_substract))
                                message = message.replace("{{credit_total}}", str(rec.store_credit))

                        action = 1
                        amount = 0
                        if rec.add_substract >= 0:
                            amount = rec.add_substract
                            action = 1
                            if to_number:
                                msg_records = self.env["msg.records"].create({"to_number": to_number,
                                                                              "message": message,
                                                                              "state": "draft",
                                                                              "current_date": current_date})
                                msg_records.send_msg_records()
                        else:
                            amount = rec.add_substract
                            action = 2

                        data_credit = {
                            "customerId": customer_id,
                            "amount": amount,
                            "action": action
                        }
                        headers = {'Content-Type': 'application/json',
                                   'Authorization': token}
                        path_store_credit = '/rest/V1/customer/storecredit'
                        api_url_store_credit = '{}{}'.format(url, path_store_credit)

                        response = requests.request("PUT", url=api_url_store_credit, headers=headers,
                                                    data=json.dumps(data_credit))

            return res


class StoreCreditHistory(models.Model):
    _name = 'store.credit.history'
    _order = "id desc"

    balance_change = fields.Float("Balance Change")
    new_balance = fields.Float("New Balance")
    partner_id = fields.Many2one('res.partner')
    user_id = fields.Many2one('res.users', "User")

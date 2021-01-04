from odoo import models, fields, api, _
import json
from datetime import date, datetime
from dateutil import relativedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    account_payment_id = fields.Many2one('account.payment', "Payments")
    is_auto_payment = fields.Boolean("Auto Payment")
    payment_method_id = fields.Many2one('sale.auot.config', string='Payment Method')
    payments_widget = fields.Text(compute='_get_payment_data')
    order_confirmation = fields.Float('Order Confirmation', compute='_compute_order_confirmation')

    @api.depends('confirmation_date', 'create_date')
    def _compute_order_confirmation(self):
        for sale in self:
            if sale.confirmation_date and sale.create_date:
                time_diff = fields.Datetime.from_string(sale.confirmation_date) - fields.Datetime.from_string(
                    sale.create_date)
                sale.order_confirmation = time_diff.days

    @api.depends('account_payment_id.move_line_ids.amount_residual')
    def _get_payment_data(self):
        for rec in self:
            rec.payments_widget = json.dumps(False)
            if rec.account_payment_id:
                if rec.account_payment_id.move_line_ids:
                    info = {'title': _('Less Payment'), 'outstanding': False, 'content': self._get_payments_vals()}
                    rec.payments_widget = json.dumps(info)

    @api.model
    def _get_payments_vals(self):
        if self.account_payment_id:
            if not self.account_payment_id.move_line_ids:
                return []
            payment_vals = []
            currency_id = self.currency_id
            for payment in self.account_payment_id.move_line_ids:
                if payment.account_id.internal_type == 'receivable':
                    payment_vals.append({
                        'name': payment.name,
                        'journal_name': payment.journal_id.name,
                        'amount': self.amount_total,
                        'currency': currency_id.symbol,
                        'digits': [69, currency_id.decimal_places],
                        'position': currency_id.position,
                        'date': payment.date,
                        'payment_id': payment.id,
                        'account_payment_id': payment.payment_id.id,
                        'move_id': payment.move_id.id,
                    })
            return payment_vals

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        auto_payment = False
        journal = self.env['account.journal'].search([('type', 'in', ('cash', 'bank'))], limit=1)
        if self.eg_magento_payment_method_id:
            if self.eg_magento_payment_method_id.is_auto_payment:
                auto_payment = True
            if self.eg_magento_payment_method_id.payment_method_id:
                journal = self.eg_magento_payment_method_id.payment_method_id.journal_id
        if self.is_auto_payment and not auto_payment:
            journal = self.payment_method_id.journal_id
        if self.is_auto_payment or auto_payment:
            payment = self.env['account.payment.method'].search([], limit=1)

            payment = self.env['account.payment'].create({'partner_id': self.partner_id.id,
                                                          'amount': self.amount_total,
                                                          'payment_type': 'inbound',
                                                          'partner_type': 'customer',
                                                          'journal_id': journal.id,
                                                          'payment_method_id': payment.id,
                                                          })

            payment.post()
            self.account_payment_id = payment.id
            self.payment_status = 'paid'

        return res

    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        if self.account_payment_id:
            self.account_payment_id.cancel()
        return res


class MagentoPaymentMethod(models.Model):
    _inherit = 'magento.payment.method'

    is_auto_payment = fields.Boolean("Auto Payment")
    payment_method_id = fields.Many2one('sale.auot.config', string='Payment Method')
    english_name = fields.Char("English Name")

    def name_get(self):
        result = []
        for record in self:
            if record.english_name:
                result.append((record.id, u"%s (%s)" % (record.name, record.english_name)))
            else:
                result.append((record.id, u"%s" % (record.name)))
        return result


class SaleAutoConfig(models.Model):
    _name = 'sale.auot.config'

    name = fields.Char("Name", required=True)
    journal_id = fields.Many2one("account.journal", string='Payment Method', required=True)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def _action_launch_procurement_rule(self):
        res = super(SaleOrderLine, self)._action_launch_procurement_rule()
        for line in self:
            if line.order_id:
                if line.order_id.picking_ids and line.order_id.eg_magento_payment_method_id:
                    for picking in line.order_id.picking_ids:
                        if not picking.eg_magento_payment_method_id:
                            picking.eg_magento_payment_method_id = line.order_id.eg_magento_payment_method_id.id
        return res

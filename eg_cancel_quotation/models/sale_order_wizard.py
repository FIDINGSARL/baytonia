from odoo import api, models, _
from odoo.exceptions import UserError


class CancelSaleOrder(models.TransientModel):
    _name = 'sale.order.wizard'
    _description = 'Sale Order Wizard'

    @api.multi
    def cancel_quotation_order(self):
        sale_orders = self.env['sale.order'].browse(
            self._context.get('active_ids', []))
        for record in sale_orders:
            if record.state in ['draft']:
                record.action_cancel()
            elif record.state in ['sale'] and self.env.user.has_group('eg_cancel_quotation.group_cancel_sale_order'):
                record.action_cancel()
            elif not self.env.user.has_group('eg_cancel_quotation.group_cancel_sale_order') and \
                    record.state in ['sale']:
                raise UserError(
                    _('You do not have access to cancel the confirm sale order :%s') % record.name)
            elif record.state in ['cancel']:
                raise UserError(
                    _('Sale Order is already in a cancel state :%s.') % record.name)

            else:
                raise UserError(
                    _('You can cancel only quotation and confirm state sale orders :%s.') % record.name)

    @api.multi
    def confirm_sale_order(self):
        sale_orders = self.env['sale.order'].browse(
            self._context.get('active_ids', []))
        for record in sale_orders:
            if record.state in ['draft'] and self.env.user.has_group('eg_cancel_quotation.group_confirm_sale_order'):
                record.action_confirm()
            elif record.state in ['draft'] and not self.env.user.has_group(
                    'eg_cancel_quotation.group_confirm_sale_order'):
                raise UserError(
                    _('You do not have access to confirm the sale order :%s') % record.name)

            elif record.state in ['sale']:
                raise UserError(
                    _('Sale Order is already in a confirm state :%s') % record.name)

            elif record.state in ['cancel'] and self.env.user.has_group(
                    'eg_cancel_quotation.group_confirm_cancel_sale_order'):
                record.action_draft()
                if record.state in ['draft']:
                    record.action_confirm()

            elif record.state in ['cancel'] and not self.env.user.has_group(
                    'eg_cancel_quotation.group_confirm_cancel_sale_order'):
                raise UserError(
                    _('You do not have access to confirm the cancel sale order :%s') % record.name)
            else:
                raise UserError(
                    _('You can confirm only quotation and cancel state sale orders :%s') % record.name)

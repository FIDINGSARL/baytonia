from odoo import models, fields, api
from odoo.api import Environment


class SaleWorkflowProcess(models.Model):
    _inherit = "sale.workflow.process.ept"

    validate_order_status_ids = fields.Many2many('import.order.status', string="Validate Order Status",
                                                 help="Selected status orders will be auto validated from WooCommerce")

    @api.model
    def auto_workflow_process(self, auto_workflow_process_id=False, ids=[]):
        transaction_log_obj = self.env['transaction.log.ept']
        with Environment.manage():
            env_thread1 = Environment(self._cr, self._uid, self._context)
            sale_order_obj = env_thread1['sale.order']
            sale_order_line_obj = env_thread1['sale.order.line']
            account_payment_obj = env_thread1['account.payment']
            workflow_process_obj = env_thread1['sale.workflow.process.ept']
            if not auto_workflow_process_id:
                work_flow_process_records = workflow_process_obj.search([])
            else:
                work_flow_process_records = workflow_process_obj.browse(auto_workflow_process_id)

            if not work_flow_process_records:
                return True

            for work_flow_process_record in work_flow_process_records:
                if not ids:
                    orders = sale_order_obj.search([('auto_workflow_process_id', '=', work_flow_process_record.id),
                                                    ('state', 'not in', ('done', 'cancel', 'sale')),
                                                    ('invoice_status', '!=', 'invoiced')])  # ('invoiced','=',False)
                else:
                    orders = sale_order_obj.search(
                        [('auto_workflow_process_id', '=', work_flow_process_record.id), ('id', 'in', ids)])
                if not orders:
                    continue
                for order in orders:
                    if order.invoice_status and order.invoice_status == 'invoiced':
                        continue
                    status_ids = work_flow_process_record.validate_order_status_ids
                    if work_flow_process_record.validate_order and (
                            not status_ids or order.imported_woo_order_status in status_ids.mapped('status')):
                        try:
                            order.action_confirm()
                            order.write({'confirmation_date': order.date_order})

                        except Exception as e:
                            transaction_log_obj.create({
                                'message': "Error while confirm Sale Order %s\n%s" % (order.name, e),
                                'mismatch_details': True,
                                'type': 'sales'
                            })
                            order.state = 'draft'
                            continue
                    if work_flow_process_record.invoice_policy == 'delivery':
                        continue
                    if not work_flow_process_record.invoice_policy and not sale_order_line_obj.search(
                            [('product_id.invoice_policy', '!=', 'delivery'), ('order_id', 'in', order.ids)]):
                        continue
                    if not order.invoice_ids:
                        if work_flow_process_record.create_invoice:
                            try:
                                order.action_invoice_create()
                            except Exception as e:
                                transaction_log_obj.create({
                                    'message': "Error while Create invoice for Order %s\n%s" % (order.name, e),
                                    'mismatch_details': True,
                                    'type': 'invoice'
                                })
                                continue
                    if work_flow_process_record.validate_invoice:
                        for invoice in order.invoice_ids:
                            try:
                                invoice.action_invoice_open()
                            except Exception as e:
                                transaction_log_obj.create({
                                    'message': "Error while open Invoice for Order %s\n%s" % (order.name, e),
                                    'mismatch_details': True,
                                    'type': 'invoice'
                                })
                                continue
                            if work_flow_process_record.register_payment:
                                if invoice.residual:
                                    # Create Invoice and Make Payment
                                    vals = {
                                        'journal_id': work_flow_process_record.journal_id.id,
                                        'invoice_ids': [(6, 0, [invoice.id])],
                                        'communication': invoice.reference,
                                        'currency_id': invoice.currency_id.id,
                                        'payment_type': 'inbound',
                                        'partner_id': invoice.commercial_partner_id.id,
                                        'amount': invoice.residual,
                                        'payment_method_id': work_flow_process_record.journal_id.inbound_payment_method_ids.id,
                                        'partner_type': 'customer'
                                    }
                                    try:
                                        new_rec = account_payment_obj.create(vals)
                                        new_rec.post()
                                    except Exception as e:
                                        transaction_log_obj.create({
                                            'message': "Error while Validating Invoice for Order %s\n%s" % (
                                                order.name, e),
                                            'mismatch_details': True,
                                            'type': 'invoice'
                                        })
                                        continue
        return True

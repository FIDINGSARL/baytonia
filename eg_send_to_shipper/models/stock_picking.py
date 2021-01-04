from odoo import models, api, fields, _
from odoo.exceptions import UserError, ValidationError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    invoice_id = fields.Many2one("account.invoice", string="Invoice", readonly=1)
    eg_cod_amount = fields.Float(string="COD Amount")
    return_carrier_id = fields.Many2one("delivery.carrier", string="Return Carrier")
    return_tracking_ref = fields.Char("Return Tracking ref")

    @api.multi
    def action_done(self):
        res = super(StockPicking, self).action_done()
        if res:
            for rec in self:
                if rec.sale_id and rec.picking_type_code == 'outgoing' and rec.sale_id.eg_magento_payment_method_id.code == 'COD':
                    attachments = []
                    invoice_id = rec.sale_id.action_invoice_create()
                    rec.invoice_id = invoice_id[0]
                    if rec.invoice_id and rec.invoice_id.amount_total > 0:
                        rec.invoice_id.action_invoice_open()
                    inv_template_id = self.env['ir.actions.report']._get_report_from_name(
                        'account.report_invoice_with_payments')
                    if inv_template_id:
                        result = self.generate_attachment_of_report(inv_template_id, rec.invoice_id)
                        attachments.append((self.invoice_id.number.replace("/", "_") + '.pdf', result))
                        msg = "Invoice {}".format(rec.invoice_id.number)
                        rec.message_post(
                            body=msg,
                            subject="Attachments of Invoice",
                            attachments=attachments
                        )
        return res

    @api.multi
    def create_invoice_from_do(self):
        for rec in self:
            # if rec.sale_id and rec.picking_type_code == 'outgoing' and (
            #         rec.sale_id.payment_gateway_id or rec.sale_id.eg_magento_payment_method_id):
            if rec.sale_id and rec.picking_type_code == 'outgoing' and (rec.sale_id.eg_magento_payment_method_id):
                attachments = []
                invoice_id = rec.sale_id.action_invoice_create()
                rec.invoice_id = invoice_id[0]
                rec.invoice_id.action_invoice_open()
                inv_template_id = self.env['ir.actions.report']._get_report_from_name(
                    'account.report_invoice_with_payments')
                if inv_template_id:
                    result = self.generate_attachment_of_report(inv_template_id, rec.invoice_id)
                    attachments.append((self.invoice_id.number.replace("/", "_") + '.pdf', result))
                    msg = "Invoice {}".format(rec.invoice_id.number)
                    rec.message_post(
                        body=msg,
                        subject="Attachments of Invoice",
                        attachments=attachments
                    )

    # @api.multi
    # def button_validate(self):
    #     res = super(StockPicking, self).button_validate()
    #     if not res:
    #         for rec in self:
    #             if rec.sale_id:
    #                 attachments = []
    #                 invoice_id = rec.sale_id.action_invoice_create()
    #                 rec.invoice_id = invoice_id[0]
    #                 rec.invoice_id.action_invoice_open()
    #                 inv_template_id = self.env['ir.actions.report']._get_report_from_name(
    #                     'account.report_invoice_with_payments')
    #                 if inv_template_id:
    #                     result = self.generate_attachment_of_report(inv_template_id, rec.invoice_id)
    #                     attachments.append((self.invoice_id.number.replace("/", "_") + '.pdf', result))
    #                     msg = "Invoice {}".format(rec.invoice_id.number)
    #                     rec.message_post(
    #                         body=msg,
    #                         subject="Attachments of Invoice",
    #                         attachments=attachments
    #                     )
    #     return res

    @api.multi
    def generate_attachment_of_report(self, report, res_id):
        """
        This will render report and retrun us attachment of report
        Author : Dhaval Chauhan
        :param report: Report Template of which attachment need to be created
        :param res_id: object that need to be used while rendering
        :return: attachment record
        """
        if report.report_type not in ['qweb-html', 'qweb-pdf']:
            raise UserError(_('Unsupported report type %s found.') % report.report_type)
        result, file_format = report.render_qweb_pdf([res_id.id])

        return result

    @api.multi
    def send_to_shipper(self):
        if self._context.get('button') == 'true':
            res = super(StockPicking, self).send_to_shipper()
            return res
        elif self._context.get('manual'):
            if self.sale_id.eg_magento_payment_method_id and \
                    self.sale_id.eg_magento_payment_method_id.code in ["cod", "COD"]:
                if not self.invoice_id:
                    raise ValidationError("With COD order invoice is must")
            action = self.env.ref('eg_send_to_shipper.wizard_action_wizard_send_to_shipper').read()[0]
            return action
        else:
            return

    @api.multi
    def regenerate_delivery_label(self):
        return True

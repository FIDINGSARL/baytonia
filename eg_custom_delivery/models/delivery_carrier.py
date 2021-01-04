import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(selection_add=[("eg_custom_deliver", "Custom Delivery")])

    @api.model
    def eg_custom_deliver_send_shipping(self, pickings):
        boxes = pickings.boxes
        tracking=[]
        tracking_number = self.env['ir.sequence'].next_by_code('custom.delivery.tracking')
        for box in range(1,boxes+1):
            if boxes == 1:
                tracking_number_box = tracking_number
            else:
                tracking_number_box = tracking_number+'-'+str(box)
            pickings.write(
                {
                    'carrier_tracking_ref': tracking_number_box
                })
            tracking.append(tracking_number_box)
            slip_template_id = self.env['ir.actions.report']._get_report_from_name(
                'eg_custom_delivery.report_eg_custom_deliveryslip')
            if slip_template_id:
                attachments = []
                result = self.generate_attachment_of_report(slip_template_id, pickings)
                attachments.append((self.name.replace("/", "_") + '.pdf', result))
                msg = "Delivery Slip for {}".format(self.name)
                pickings.message_post(
                    body=msg,
                    subject="Delivery Slip for {}".format(self.name),
                    attachments=attachments
                )

        tracking_ref = ','.join(tracking)
        pickings.write(
            {
                'carrier_tracking_ref': tracking_ref
            })
        shipping_data = {'exact_price': 0, 'tracking_number': tracking_ref}
        return [shipping_data]

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

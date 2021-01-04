import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class MassMailing(models.Model):
    _inherit = 'mail.mass_mailing'

    auto_retry = fields.Boolean("Auto Retry", default=True)

    @api.multi
    def send_mail_retry_cron(self):
        mass_mail_ids = self.search([('state', 'in', ['done']), ('auto_retry', '=', True)])
        for mass_mail_id in mass_mail_ids:
            if mass_mail_id.state in ['done'] and mass_mail_id.failed > 0:
                _logger.info(["===========>>>>>>>>>>>>", mass_mail_id.name, "<<<<<<<<<<=============="])
                mass_mail_id.retry_failed_mail()

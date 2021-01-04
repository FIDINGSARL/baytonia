from odoo import api, fields, models

import logging

_logger = logging.getLogger(__name__)


class WkSkeleton(models.TransientModel):
    _inherit = 'wk.skeleton'


    @api.model
    def create_order(self, saleData):
        _logger.info(["create order ", saleData])
        magento_customer = self.env['magento.customers'].search([('oe_customer_id', '=', saleData.get('partner_id'))])
        if magento_customer:
            return super(WkSkeleton, self).create_order(saleData)
        else:
            customer = self.env['res.partner'].search(
                [('id', '=', saleData.get('partner_id'))])
            if customer:
                email = customer.email
                existing_customer = self.env['res.partner'].search(
                    [('email', '=', email),('parent_id', '=', False)],limit=1)
                _logger.info(["Existing Customer", existing_customer])

                if existing_customer:
                    customer_invoice = self.env['res.partner'].search(
                        [('id', '=', saleData.get('partner_invoice_id'))])
                    saleData['partner_id'] = existing_customer.id
                    return super(WkSkeleton, self).create_order(saleData)
                else:
                    return super(WkSkeleton, self).create_order(saleData)
            else:
                return super(WkSkeleton, self).create_order(saleData)


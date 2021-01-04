from odoo import api, models


class BridgeBackbone(models.TransientModel):
    _inherit = "bridge.backbone"

    @api.model
    def create_payment_method(self, data):
        """Method to create magento payment method to use for other purposes
        """
        res = super(BridgeBackbone, self).create_payment_method(data)
        magento_payment_method = self.env['magento.payment.method']
        m_payment_method_id = magento_payment_method.search([('name', '=', data.get('name'))])
        if not m_payment_method_id:
            odoo_payment_method_id = self.env["account.journal"].browse(res)
            payment_vals = {
                'name': data.get('name'),
                'odoo_payment_id': res,
                'code': odoo_payment_method_id.code
            }
            magento_payment_method.create(payment_vals)
        elif m_payment_method_id:
            m_payment_method_id.odoo_payment_id = res
        return res

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class MagentoConfigure(models.Model):
    _inherit = "magento.configure"

    category_sync = fields.Boolean(string="Category Sync")
    product_image_sync = fields.Boolean(string="Product Image Sync")
    description_sync = fields.Boolean(string="Description Sync")
    short_description_sync = fields.Boolean(string="Short Description Sync")
    auto_order_status_update = fields.Boolean(string="Auto update order status")
    confirmation_states = fields.Char(string="Auto confirm states", help="Add state code ',' comma separated")
    manage_back_order = fields.Boolean(string="Manage Back order")
    manage_product_status = fields.Boolean(string="Manage Product status")

    @api.model
    def _create_connection(self):
        """ create a connection between Odoo and magento
                returns: False or list"""
        instanceId = self._context.get('instance_id', False)
        token = ''
        if instanceId:
            instanceObj = self.browse(instanceId)
        else:
            activeConnections = self.search([('active', '=', True)])
            if len(activeConnections) > 1:
                raise UserError(
                    _('Error!\nSorry, only one Active Configuration setting is allowed.'))
            if not activeConnections:
                raise UserError(
                    _('Error!\nPlease create the configuration part for Magento connection!!!'))
            else:
                instanceObj = activeConnections[0]
        token_generation = instanceObj.create_magento_connection()
        if token_generation:
            if len(token_generation[0]) > 1:
                if token_generation[0][0]:
                    token = token_generation[0][0]
        if token:
            return [instanceObj.name, token, instanceObj.id]
        else:
            return False

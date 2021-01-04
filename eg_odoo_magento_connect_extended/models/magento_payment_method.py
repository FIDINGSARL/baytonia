from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MagentoPaymentMethod(models.Model):
    _name = "magento.payment.method"

    name = fields.Char("Name")
    code = fields.Char("Code")
    odoo_payment_id = fields.Many2one("account.journal", "Odoo Payment Method")
    product_id = fields.Many2one("product.product", "Charges Product", help="i.e. COD changes product")
    charges = fields.Float("Charges")
    auto_process = fields.Boolean("Auto Process")
    eg_invoice_policy = fields.Selection([('order', 'Ordered quantities'), ('delivery', 'Delivered quantities')],
                                         string='Invoicing Policy', default="delivery")
    auto_invoice = fields.Boolean("Auto Invoice")
    auto_register = fields.Boolean("Auto Validate")
    register_popup = fields.Boolean("Register popup")
    journal_id = fields.Many2one('account.journal', 'Journal', help="Payment will be registered with this Journal")

    @api.onchange('eg_invoice_policy')
    def _onchange_eg_invoice_policy(self):
        if self.eg_invoice_policy == "delivery":
            self.auto_register = False
            self.journal_id = False
            self.auto_invoice = False

    @api.onchange('eg_invoice_policy', 'auto_invoice')
    def _onchange_auto_invoice_policy(self):
        if self.auto_invoice and self.eg_invoice_policy == "delivery":
            raise ValidationError("You can not make auto invoice with Delivered quantities policy!!!")

    @api.onchange('auto_invoice')
    def _onchange_auto_invoice(self):
        self.auto_register = False
        self.journal_id = False

    @api.onchange("auto_register")
    def _onchange_auto_register(self):
        self.journal_id = False
        self.register_popup = False

    @api.onchange("register_popup")
    def _onchange_register_popup(self):
        self.journal_id = False
        self.auto_register = False

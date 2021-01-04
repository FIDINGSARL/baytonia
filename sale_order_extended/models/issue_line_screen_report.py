from odoo import models, fields, api
from datetime import datetime, date
import odoo


class IssueLineReport(models.TransientModel):
    _name = "issue.line.screen.report"

    serial_no = fields.Integer('Serial No')
    reason_id = fields.Many2one(comodel_name="issue.reason", string="Reason")
    order_id = fields.Many2one(comodel_name="sale.order", string="Sale Order")
    sale_line_id = fields.Many2one(comodel_name="sale.order.line", string="Order Line")
    product_id = fields.Many2one(comodel_name="product.product", string="Product")
    order_qty = fields.Float(string="Quantity")
    unit_price = fields.Float(string="Unit Price")
    generate_date = fields.Datetime(string="Generate Date", default=datetime.now())
    responsible_id = fields.Many2one(comodel_name="res.users", string="Responsible Person")
    confirm_person_id = fields.Many2one(comodel_name="res.users", string="Confirm By")
    carrier_id = fields.Many2one(comodel_name="delivery.carrier", string="Shipping Company")
    image_small = fields.Binary('Image')
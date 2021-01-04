# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2017-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################


from odoo import _, models, fields
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _name = 'stock.picking'
    _inherit = ['stock.picking', 'barcodes.barcode_events_mixin']

    barcode_scan = fields.Boolean(string="Barcode Scan")

    def on_barcode_scanned(self, barcode):
        if not self.barcode_scan:
            self.barcode_scan = True
        product = self.env['product.product'].search(['|', ('barcode', '=', barcode), ('default_code', '=', barcode)])
        if product:
            moveLineObjs = self.move_line_ids.filtered(
                lambda r: r.product_id == product)
            move_lines = self.move_lines.filtered(
                lambda r: r.product_id == product)
            if moveLineObjs:
                for moveLineObj in moveLineObjs:
                    if moveLineObj.qty_done < moveLineObj.product_qty:
                        moveLineObj.qty_done += 1
                        break
                    elif moveLineObj == moveLineObjs[-1]:
                        raise UserError(
                            _('You are trying to deliver quantity more than ordered.'))
            elif move_lines:
                stateLabel = dict(
                    self.move_line_ids.fields_get('state')['state']['selection']).get(
                    move_lines[0].state, '')
                raise UserError(
                    _('Scanned product %s with barcode %s is present in this picking but currently in "%s" state.') %
                    (product.display_name, barcode, stateLabel))
            else:
                raise UserError(
                    _('This product %s with barcode %s is not present in this picking.') %
                    (product.name, barcode))
        else:
            raise UserError(
                _('This barcode %s is not related to any product.') %
                barcode)

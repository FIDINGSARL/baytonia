# -*- coding: utf-8 -*-
##############################################################################
#
#    Sahil Navadiya
#    Copyright (C) 2018-TODAY (<navadiyasahil@gmail.com>).
#
##############################################################################

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def _action_confirm(self):
        res = super(SaleOrder, self)._action_confirm()

        send_to = self.partner_id.mobile or self.partner_id.phone
        if not send_to:
            send_to = self.partner_id.parent_id.mobile or self.partner_id.parent_id.phone

        # _logger.info("\n\nSend TO : %s",send_to)

        if self.state == "sale" and send_to:
            try:
                infobip = self.env['fl.infobip.sms'].search([('active', '=', True)])
                if infobip and infobip.confirm_order_message:
                    txt = "%s Order Ref : %s" % (infobip.confirm_order_message, self.name)
                    # _logger.info("\n\nhere in if : %s",txt)
                    # self.env['fl.infobip.sms'].send_sms("Your order #%s is confirmed"%(self.name), send_to, True)
                    self.env['fl.infobip.sms'].send_sms(txt, send_to.split('+', 1)[-1], True)
            except:
                pass
        return res


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def action_done(self):
        res = super(StockPicking, self).action_done()

        send_to = self.partner_id.mobile or self.partner_id.phone
        if not send_to:
            send_to = self.partner_id.parent_id.mobile or self.partner_id.parent_id.phone

        # _logger.info("\n\nSend TO : %s",send_to)

        if self.state == "done" and send_to and self.carrier_tracking_ref:

            try:
                infobip = self.env['fl.infobip.sms'].search([('active', '=', True)])
                if infobip and infobip.delivery_confirm_message:
                    link_tracker_id = self.env['link.tracker'].search([('sale_id', '=', self.sale_id.id)])
                    if not link_tracker_id and self.sale_id.carrier_details:
                        link_tracker_id = self.env['link.tracker'].create({
                            'title': self.sale_id.name,
                            'sale_id': self.sale_id.id,
                            'url': self.sale_id.carrier_details
                        })

                    msg = "طلبك من بيتونيا {} في طريقه لك مع شركة {} و رقم التتبع هو {}".format(
                        self.sale_id.woo_order_number, self.carrier_id.name,
                        link_tracker_id.url and link_tracker_id.short_url or self.sale_id.carrier_details or "")
                    self.env['fl.infobip.sms'].send_sms_url(msg, send_to.split('+', 1)[-1], True)
            except:
                pass
        return res


class InfobipSms(models.Model):
    _inherit = "fl.infobip.sms"

    confirm_order_message = fields.Text(string="Confirm Order Message", default="Your order is confirmed.")
    delivery_confirm_message = fields.Text(string="Delivery Order Confirm Message",
                                           default="Your order is out for delivery. ")


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    tracking_url = fields.Text(string="Tracking URL")

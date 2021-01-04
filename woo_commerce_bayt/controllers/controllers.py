# -*- coding: utf-8 -*-
from odoo import http

# class BaytWoo(http.Controller):
#     @http.route('/woo_commerce_bayt/woo_commerce_bayt/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/woo_commerce_bayt/woo_commerce_bayt/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('woo_commerce_bayt.listing', {
#             'root': '/woo_commerce_bayt/woo_commerce_bayt',
#             'objects': http.request.env['woo_commerce_bayt.woo_commerce_bayt'].search([]),
#         })

#     @http.route('/woo_commerce_bayt/woo_commerce_bayt/objects/<model("woo_commerce_bayt.woo_commerce_bayt"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('woo_commerce_bayt.object', {
#             'object': obj
#         })
from odoo import models,fields,api

class stock_location_route(models.Model):
    _inherit="stock.location.route"
    #Added by AG

    export_stock_to_woo = fields.Boolean("Export Stock To Woo",default=True,help="If True, Stock will be exported for this product route.")
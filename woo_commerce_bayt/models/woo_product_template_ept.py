from odoo import models,fields,api

class woo_product_template_ept(models.Model):
    _inherit="woo.product.template.ept"
    #Extension created by AG for stock export for selected routes

    export_to_woo = fields.Boolean("Export To Woo")
                                   # , compute="get_export_to_woo",store=True)

    @api.multi
    def get_export_to_woo(self):
        """
        This method calculates if product stock can be exported to woo or not.
        Create by AG
        """
        for record in self:
            export = True
            for route in record.product_tmpl_id.route_ids:
                if not route.export_stock_to_woo:
                    export = False
                    break
            record.export_to_woo = export

    @api.model
    def update_new_stock_in_woo(self, instance=False, products=False):
        """
        This method removes product whose stock should not be exported based on route settings
        Create by AG
        """
        if products:
            products = products.filtered(lambda wp: wp.export_to_woo)
        return super(woo_product_template_ept,self).update_new_stock_in_woo(instance,products)
from odoo import models,fields,api

class ResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    use_average_sale_to_cal_growth = fields.Boolean("Use Average Sales To Calculate Growth")
    past_x_days_sale = fields.Char("Check Past X days Sale")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            use_average_sale_to_cal_growth=self.env['ir.config_parameter'].sudo().get_param('top_growing_product.use_average_sale_to_cal_growth'),
            past_x_days_sale=self.env['ir.config_parameter'].sudo().get_param('top_growing_product.past_x_days_sale')
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            'top_growing_product.use_average_sale_to_cal_growth',self.use_average_sale_to_cal_growth),
        self.env['ir.config_parameter'].sudo().set_param('top_growing_product.past_x_days_sale', self.past_x_days_sale)
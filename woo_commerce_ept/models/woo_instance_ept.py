from odoo import models,fields,api,_
from odoo.exceptions import Warning
from .. import woocommerce
import requests

class woo_instance_ept(models.Model):
    _name="woo.instance.ept"
    _description = "WooCommerce Instance"
    
    @api.model
    def _default_stock_field(self):
        qty_available = self.env['ir.model.fields'].search([('model_id.model','=','product.product'),('name','=','qty_available')],limit=1)
        return qty_available and qty_available.id
    
    name = fields.Char(size=120, string='Name', required=True)
    company_id = fields.Many2one('res.company',string='Company', required=True)
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist')
    lang_id = fields.Many2one('res.lang', string='Language')
    order_prefix = fields.Char(size=10, string='Order Prefix')
    import_order_status_ids = fields.Many2many('import.order.status','woo_instance_order_status_rel','instance_id','status_id',"Import Order Status",help="Selected status orders will be imported from WooCommerce")
    order_auto_import = fields.Boolean(string='Auto Order Import?')
    order_auto_update=fields.Boolean(string="Auto Order Update ?")
    stock_auto_export=fields.Boolean(string="Stock Auto Export?")    
    fiscal_position_id = fields.Many2one('account.fiscal.position', string='Fiscal Position')
    stock_field = fields.Many2one('ir.model.fields', string='Stock Field', default=_default_stock_field)
    country_id=fields.Many2one("res.country","Country")
    host=fields.Char("Host",required=True)    
    auto_import_product = fields.Boolean(string="Auto Create Product if not found?")
    consumer_key=fields.Char("Consumer Key",required=True,help="Login into WooCommerce site,Go to Admin Panel >> WooCommerce >> Settings >> API >> Keys/Apps >> Click on Add Key")
    consumer_secret=fields.Char("Consumer Secret",required=True,help="Login into WooCommerce site,Go to Admin Panel >> WooCommerce >> Settings >> API >> Keys/Apps >> Click on Add Key")
    verify_ssl=fields.Boolean("Verify SSL",default=False,help="Check this if your WooCommerce site is using SSL certificate")      
    section_id=fields.Many2one('crm.team', 'Sales Team')
    payment_term_id = fields.Many2one('account.payment.term', string='Payment Term')    
    discount_product_id=fields.Many2one("product.product","Discount",domain=[('type','=','service')])
    fee_line_id=fields.Many2one("product.product","Fees",domain=[('type','=','service')])    
    last_inventory_update_time=fields.Datetime("Last Inventory Update Time")    
    state=fields.Selection([('not_confirmed','Not Confirmed'),('confirmed','Confirmed')],default='not_confirmed')
    is_image_url = fields.Boolean("Is Image URL?",help="Check this if you use Images from URL\nKepp as it is if you use Product images")
    admin_username=fields.Char("Username", help="WooCommerce UserName,Used to Export Image Files.")
    admin_password=fields.Char("Password", help="WooCommerce Password,Used to Export Image Files.")
    woo_version = fields.Selection([('new','2.6+'),('old','<=2.6')],default='old',string="WooCommerce Version",help="Set the appropriate WooCommerce Version you are using currently or\nLogin into WooCommerce site,Go to Admin Panel >> Plugins")
    is_latest=fields.Boolean('3.0 or later',default=False)
    is_set_price = fields.Boolean(string="Set Price ?",default=False)
    is_set_stock = fields.Boolean(string="Set Stock ?",default=False)
    is_publish = fields.Boolean(string="Publish In Website ?",default=False)
    is_set_image = fields.Boolean(string="Set Image ?",default=False)
    sync_images_with_product=fields.Boolean("Sync Images?",help="Check if you want to import images along with products",default=False)
    sync_price_with_product=fields.Boolean("Sync Product Price?",help="Check if you want to import price along with products",default=False)
    is_show_debug_info=fields.Boolean('Show Debug Information?',default=False)
    inventory_adjustment_id=fields.Many2one('stock.inventory',"Last Inventory")
    visible = fields.Boolean("Visible on the product page?",default=True,help="""Attribute is visible on the product page""")
    variation = fields.Boolean("Attribute used as a variations?",default=True,help="""Attribute can be used as variation?""")
    attribute_type=fields.Selection([('select', 'Select'), ('text', 'Text')], string='Attribute Type',default='text')
    
    def _count_all(self):
        for instance in self:
            instance.product_count = len(instance.product_ids)
            instance.sale_order_count = len(instance.sale_order_ids)
            instance.picking_count = len(instance.picking_ids)
            instance.invoice_count = len(instance.invoice_ids)
            instance.exported_product_count = len(instance.exported_product_ids)
            instance.ready_to_expor_product_count = len(instance.ready_to_expor_product_ids)
            instance.published_product_count = len(instance.published_product_ids)
            instance.unpublished_product_count = len(instance.unpublished_product_ids)
            instance.quotation_count = len(instance.quotation_ids)
            instance.order_count = len(instance.order_ids)
            instance.confirmed_picking_count = len(instance.confirmed_picking_ids)
            instance.assigned_picking_count = len(instance.assigned_picking_ids)
            instance.partially_available_picking_count = len(instance.partially_available_picking_ids)
            instance.done_picking_count = len(instance.done_picking_ids)
            instance.open_invoice_count = len(instance.open_invoice_ids)
            instance.paid_invoice_count = len(instance.paid_invoice_ids)
            instance.refund_invoice_count = len(instance.refund_invoice_ids)  
            instance.coupons_count = len(instance.coupons_ids)          
    
    color = fields.Integer(string='Color Index')
    
    exported_product_ids = fields.One2many('woo.product.template.ept','woo_instance_id',domain=[('exported_in_woo','=',True)],string="Exported Products")
    exported_product_count = fields.Integer(compute='_count_all', string="Exported Products")
    
    ready_to_expor_product_ids = fields.One2many('woo.product.template.ept','woo_instance_id',domain=[('exported_in_woo','=',False)],string="Ready To Export")
    ready_to_expor_product_count = fields.Integer(compute='_count_all', string="Ready To Export")
    
    published_product_ids = fields.One2many('woo.product.template.ept','woo_instance_id',domain=[('website_published','=',True)],string="Published")
    published_product_count = fields.Integer(compute='_count_all', string="Published")
    
    unpublished_product_ids = fields.One2many('woo.product.template.ept','woo_instance_id',domain=[('website_published','=',False),('exported_in_woo','=',True)],string="Published")
    unpublished_product_count = fields.Integer(compute='_count_all', string="UnPublished")
    
    quotation_ids = fields.One2many('sale.order','woo_instance_id',domain=[('state','in',['draft','sent'])],string="Quotations")        
    quotation_count = fields.Integer(compute='_count_all', string="Quotations")
        
    order_ids = fields.One2many('sale.order','woo_instance_id',domain=[('state','not in',['draft','sent','cancel'])],string="Sales Order")
    order_count = fields.Integer(compute='_count_all', string="Sales Order")
    
    coupons_ids = fields.One2many('woo.coupons.ept','woo_instance_id',domain=[('exported_in_woo','=',True)],string="Coupons")
    coupons_count = fields.Integer(compute='_count_all', string="Coupons")
    
    confirmed_picking_ids = fields.One2many('stock.picking','woo_instance_id',domain=[('state','=','confirmed')],string="Confirm Pickings")
    confirmed_picking_count =fields.Integer(compute='_count_all', string="Confirm Pickings")
    assigned_picking_ids = fields.One2many('stock.picking','woo_instance_id',domain=[('state','=','assigned')],string="Assigned Pickings")
    assigned_picking_count =fields.Integer(compute='_count_all', string="Assigned Pickings")
    partially_available_picking_ids = fields.One2many('stock.picking','woo_instance_id',domain=[('state','=','partially_available')],string="Partially Available Pickings")
    partially_available_picking_count =fields.Integer(compute='_count_all', string="Partially Available Pickings")
    done_picking_ids = fields.One2many('stock.picking','woo_instance_id',domain=[('state','=','done')],string="Done Pickings")
    done_picking_count =fields.Integer(compute='_count_all', string="Done Pickings")
    
    open_invoice_ids = fields.One2many('account.invoice','woo_instance_id',domain=[('state','=','open'),('type','=','out_invoice')],string="Open Invoices")
    open_invoice_count =fields.Integer(compute='_count_all', string="Open Invoices")    

    paid_invoice_ids = fields.One2many('account.invoice','woo_instance_id',domain=[('state','=','paid'),('type','=','out_invoice')],string="Paid Invoices")
    paid_invoice_count =fields.Integer(compute='_count_all', string="Paid Invoices")
    
    refund_invoice_ids = fields.One2many('account.invoice','woo_instance_id',domain=[('type','=','out_refund')],string="Refund Invoices")
    refund_invoice_count =fields.Integer(compute='_count_all', string="Refund Invoices")
    
    product_ids = fields.One2many('woo.product.template.ept','woo_instance_id',string="Products")
    product_count = fields.Integer(compute='_count_all', string="Products")
    
    sale_order_ids = fields.One2many('sale.order','woo_instance_id',string="Orders")
    sale_order_count = fields.Integer(compute='_count_all', string="Products")
    
    picking_ids = fields.One2many('stock.picking','woo_instance_id',string="Pickings")
    picking_count = fields.Integer(compute='_count_all', string="Pickings")
    
    invoice_ids = fields.One2many('account.invoice','woo_instance_id',string="Invoices")
    invoice_count = fields.Integer(compute='_count_all', string="Invoices")  
    
    global_channel_id = fields.Many2one('global.channel.ept',string = "Global Channel")   

    
    @api.multi
    def test_woo_connection(self):              
        wcapi = self.connect_in_woo()
        r = wcapi.get("products")
        if not isinstance(r,requests.models.Response):
            raise Warning(_("Response is not in proper format :: %s"%(r)))
        if r.status_code != 200:
            raise Warning(_("%s\n%s"%(r.status_code,r.reason)))        
        else:
            raise Warning('Service working properly')
        return True
        
    @api.multi
    def reset_to_confirm(self):
        self.write({'state':'not_confirmed'})
        return True
    
    @api.multi
    def confirm(self):        
        wcapi = self.connect_in_woo()
        r = wcapi.get("products")
        if not isinstance(r,requests.models.Response):
            raise Warning(_("Response is not in proper format :: %s"%(r)))
        if r.status_code != 200:
            raise Warning(_("%s\n%s"%(r.status_code,r.reason)))
        else:            
            self.write({'state':'confirmed'})
        return True              
        
    @api.model
    def connect_in_woo(self):
        host = self.host
        consumer_key = self.consumer_key
        consumer_secret = self.consumer_secret
        wp_api = True if self.woo_version == 'new' else False
        version = "wc/v1" if wp_api else "v3"
        if self.is_latest:
            version = "wc/v2"
        wcapi = woocommerce.api.API(url=host, consumer_key=consumer_key,
                    consumer_secret=consumer_secret,verify_ssl=self.verify_ssl,wp_api=wp_api,version=version,query_string_auth=True)
        return wcapi
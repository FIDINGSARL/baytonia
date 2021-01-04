# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "Product Advance Barcode Labels",
  "summary"              :  "This module allows user to generate product barcode labels of different size and support multiple configuration for barcode generation.",
  "category"             :  "Website",
  "version"              :  "1.0.0",
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Product-Advance-Barcode-Labels.html",
  "description"          :  """https://webkul.com/blog/odoo-product-advance-barcode-labels/""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=product_barcode_labels&version=11.0",
  "depends"              :  [
                             'stock','delivery',
                            ],
  "data"                 :  [
                                'security/ir.model.access.csv',
                                'data/res_config_settings.xml',
                                'wizard/product_label_wizard.xml',
                                'views/mp_products_view.xml',
                                'views/label_configurator_view.xml',
                                'views/product_label_template.xml',
                                'views/product_label_report.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "price"                :  35,
  "currency"             :  "EUR",
  "pre_init_hook"        :  "pre_init_check",
}

# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   @License       : https://store.webkul.com/license.html
#################################################################################
import odoo
from odoo import api, http, tools, _
from odoo.addons.web.controllers.main import content_disposition
from odoo.http import request
from datetime import datetime

import zipfile
import io

import logging
_logger = logging.getLogger(__name__)

class Binary(http.Controller):

    @http.route('/product/binary/download_labels', type='http', auth="public")
    def get_product_labels(self,model,id,**post):
        wizard = request.env[model].browse(int(id))
        label_config = wizard.l_config
        product_ids = wizard.product_ids
        paperformat_id = request.env.ref('product_barcode_labels.paperformat_product_label_report11')
        current_date = datetime.today().strftime("%Y-%m-%d at %H:%M:%S")

        if label_config:
            buff = io.BytesIO()
            archive = zipfile.ZipFile(buff,'w',zipfile.ZIP_DEFLATED)
            paperformat_id.sudo().write({
                'orientation' : label_config[0].orientation,
            })

            for product in product_ids:
                base_name = product.default_code if product.default_code else product.name

                file_like_1 = request.env.ref('product_barcode_labels.product_product_label_report11').with_context(label_config=label_config[0]).render_qweb_pdf([product.id])[0]
                labelname1 = '%s %s.pdf' % (base_name,current_date)
                archive.writestr(labelname1,file_like_1)

            archive.close()
            buff.flush()
            ret_zip = buff.getvalue()
            buff.close()

            filename = '%s %s.zip' % (label_config[0].name,current_date)
            return request.make_response(ret_zip,
                            [('Content-Type', 'application/zip'),
                             ('Content-Disposition', content_disposition(filename))])

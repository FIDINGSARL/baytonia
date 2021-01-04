# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import io
import imghdr
import functools
import odoo
from odoo.addons.web.controllers.main import db_monodb, ensure_db, set_cookie_and_redirect, login_and_redirect
from odoo import http, modules, SUPERUSER_ID, tools, _
from odoo.http import request
from odoo.modules import get_resource_path


class WebsiteForum(http.Controller):

    @http.route([ '/banners',], type='http', auth="none", cors="*")
    def training_headers(self, dbname=None, **kw):
        imgname = 'logo'
        imgext = '.png'
        placeholder = functools.partial(get_resource_path, 'web', 'static', 'src', 'img')
        uid = None
        if request.session.db:
            dbname = request.session.db
            uid = request.session.uid
        elif dbname is None:
            dbname = db_monodb()

        if not uid:
            uid = odoo.SUPERUSER_ID

        if not dbname:
            response = http.send_file(placeholder(imgname + imgext))
        else:
            try:
                # create an empty registry
                image = False
                registry = odoo.modules.registry.Registry(dbname)
                with registry.cursor() as cr:
                    training_record = int(kw['record']) if kw and kw.get('record') else False
                    cr.execute("""SELECT image_small, 
                                            FROM product_product
                                           WHERE id = %s
                                       """, (training_record,))

                    row = cr.fetchone()
                    if row and row[0]:
                        image_base64 = base64.b64decode(row[0])
                        image_data = io.BytesIO(image_base64)
                        imgext = '.' + (imghdr.what(None, h=image_base64) or 'png')
                        response = http.send_file(image_data, filename=imgname + imgext, mtime=row[1])
                    # else:
                    #     response = http.send_file(placeholder('nologo.png'))
            except Exception:
                response = http.send_file(placeholder(imgname + imgext))

        return response


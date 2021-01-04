# -*- coding: utf-8 -*-
import base64
import csv
import io
import logging
import os
import zipfile
from datetime import datetime
from io import BytesIO

from odoo import models, fields, api, tools, _
from odoo.exceptions import except_orm

_logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 100 * 1024 * 1024  # in megabytes

addons_path = os.path.abspath('/tmp/import_image')


class ProductImageImport(models.TransientModel):
    _name = 'product.image.import'

    image_file = fields.Binary(string='.ZIP file', required=True)
    filename = fields.Char('File Name')
    datas = fields.Binary('Datas')
    is_bounced = fields.Boolean(default=False)
    is_process_finished = fields.Boolean(default=False)

    def _write_bounced_images(self, file_head, bounced_detail, context):
        if not file_head:
            _logger.warning("Can not Export bounced(Rejected) Images detail to the file. ")
            return False
        try:
            dtm = datetime.today().strftime("%Y_%m_%d_%H_%M_%S")
            fname = "BOUNCED_IMAGES_" + dtm + ".csv"
            _logger.info("Opening file '%s' for logging the bounced images detail." % (fname))

            fp = io.StringIO()
            fl = csv.writer(fp, delimiter=' ', quotechar=' ', quoting=csv.QUOTE_MINIMAL)
            for ln in bounced_detail:
                fl.writerow(ln)
            csv_file = base64.encodebytes(fp.getvalue().encode())
            fp.close()
            _logger.info("Successfully exported the bounced images detail to the file %s." % (fname))
            _logger.info(["=======DATA=====", csv_file])
            return {'file_path': file_head + "/" + fname, 'fname': fname, 'file_data': csv_file}
        except Exception as e:
            _logger.warning(["Can not Export bounced(Rejected) images detail to the file. ", e])
            return False

    def load_images_from_folder(self):
        images = []
        zip_data = base64.decodestring(self.image_file)
        fp = BytesIO()
        fp.write(zip_data)
        path = self.import_zipfile(fp)
        bounced_image = []
        for filename in path:
            name = filename.split('/')[-1]
            try:
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    with open(filename, 'rb') as fp:
                        image_base64 = base64.b64encode(fp.read())
                    images.append({'filename': name, 'default_code': name.split('.')[:1][0], 'image': image_base64})
                else:
                    if not filename.lower().endswith('/'):
                        bounced_image.append(["Images has no proper extension: " + str(name)])
            except Exception:
                bounced_image.append([str(name)])
        return images, bounced_image

    @api.model
    def import_zipfile(self, module_file):
        if not module_file:
            raise Exception(_("No file sent."))
        if not zipfile.is_zipfile(module_file):
            raise except_orm(_('Error!'), _('File is not a zip file!'))

        image_list = []
        with zipfile.ZipFile(module_file, "r") as z:
            for zn in z.namelist():
                image_list.append(addons_path + '/' + zn)
            for zf in z.filelist:
                if zf.file_size > MAX_FILE_SIZE:
                    raise except_orm(_('Error!'), (_("File '%s' exceed maximum allowed file size") % zf.filename))
            # with tempdir() as module_dir:
            #     import odoo.modules as addons
            #     try:
            #         for root, dirs, files in os.walk(addons_path):
            #             for f in files:
            #                 os.unlink(os.path.join(root, f))
            #             for d in dirs:
            #                 shutil.rmtree(os.path.join(root, d))
            #         addons.module.ad_paths.append(module_dir)
            #         z.extractall(addons_path)
            #     finally:
            #         addons.module.ad_paths.remove(module_dir)
            z.extractall(addons_path)

        return image_list

    @api.multi
    def confirm_import(self):
        images_data = self.load_images_from_folder()
        Product = self.env['product.product']
        bounce_imgs = images_data[1]

        for data in images_data[0]:
            product_id = Product.search([('default_code', '=', data['default_code'])], limit=1)
            if product_id:
                data_img = tools.image_get_resized_images(data['image'], return_big=True)
                image = data_img['image']
                product_id.image = image
            else:
                bounce_imgs.append(['Product(Item number) not found: ' + str(data['filename'])])

        ctx = {}
        if bounce_imgs:
            context = {}
            file = self._write_bounced_images('/tmp', bounce_imgs, context)
            # f = open(file['file_path'])
            # f.close()
            self.datas = file.get('file_data')
            # ctx.update({'default_is_bounced': True, 'default_file': file.get('fname'),
            #             'default_file_data': file.get('file_data')})

            _logger.info("Successfully completed import process.")
            self.filename = file.get('fname')
            self.is_bounced = True
        self.is_process_finished = True
        return {
            'view_mode': 'form',
            'res_id': self.id,
            'res_model': 'product.image.import',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'context': self.env.context,
            'target': 'new',
        }

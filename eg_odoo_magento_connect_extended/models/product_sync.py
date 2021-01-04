import logging

from odoo import models

_logger = logging.getLogger("==== MOB Product E/U ====")


class MagentoSynchronization(models.TransientModel):
    _inherit = "magento.synchronization"

    ############# fetch product details ########
    def _get_product_array(self, url, token, prodObj, getProductData):
        instance_id = self.env['magento.configure'].search([('active', '=', True)])
        if instance_id.category_sync and instance_id.product_image_sync:
            return super(MagentoSynchronization, self)._get_product_array(url, token, prodObj, getProductData)

        status = 2
        if prodObj.sale_ok:
            status = 1
        getProductData.update(
            name=prodObj.name,
            weight=prodObj.weight or 0.00,
            status=status
        )
        custom_attributes = [
            {"attribute_code": "cost", "value": prodObj.standard_price or 0.00}
        ]
        if instance_id.category_sync:
            prodCategs = []
            for categobj in prodObj.categ_ids:
                mageCategId = self.sync_categories(url, token, categobj)
                if mageCategId:
                    prodCategs.append(mageCategId)
            custom_attributes.append({"attribute_code": "category_ids", "value": prodCategs})
        if instance_id.description_sync:
            custom_attributes.append({"attribute_code": "description", "value": prodObj.description})
        if instance_id.description_sync:
            custom_attributes.append({"attribute_code": "short_description", "value": prodObj.description_sale})
        if 'custom_attributes' not in getProductData:
            getProductData['custom_attributes'] = custom_attributes
        else:
            getProductData['custom_attributes'] += custom_attributes

        if instance_id.product_image_sync:
            imageData = self._get_product_media(prodObj)
            if imageData:
                getProductData.update(media_gallery_entries=[imageData])
        return getProductData

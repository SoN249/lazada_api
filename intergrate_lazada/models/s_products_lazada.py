from odoo import fields, models, api
from odoo.exceptions import ValidationError
from PIL import Image
import io, base64


class SProductLazada(models.Model):
    _inherit = ['product.template']

    brand_id = fields.Many2one('brands.lazada', string="Brand")
    package_height = fields.Float('Chiều cao (cm)', required=True)
    package_length = fields.Float('Chiều dai (cm)', required=True)
    package_width = fields.Float('Chiều rộng (cm)', required=True)
    package_weight = fields.Float('Trọng lượng', required=True)
    check_sync_product = fields.Boolean('Check sync', default=False, readonly=True)
    is_push_lazada = fields.Boolean('Push lazada', default=False, )
    warranty_type = fields.Selection([('No Warranty', "Không có bảo hành")], default='No Warranty')
    is_shipped_by_seller = fields.Selection([('No', 'Không'),
                                             ('Yes', 'Có')
                                             ], default='No')
    @api.onchange('is_push_lazada')
    def _check_is_push_lazada(self):
        if self.is_push_lazada:
            if len(self.attribute_line_ids.attribute_id) > 2:
                self.is_push_lazada = False
                return {
                    'warning': {
                        'title': 'Cảnh báo',
                        'message': 'Chỉ có 2 biến thể mới có thể được đẩy lên lazada'
                    }
                }

    # Upload image product
    def upload_image_lazada(self, img):
        api = "/image/upload"
        height_resize, with_resize = 0, 0
        img = Image.open(io.BytesIO(base64.decodebytes(bytes(img.decode('ascii'), "utf-8")))).convert('RGB')
        if img.height < 330:
            height_resize = 330 - img.height
        if img.width < 330:
            with_resize = 330 - img.width
        img_resize = img.resize((img.height + height_resize, img.width + with_resize))
        img_resize.save('customaddons/intergrate_lazada/static/img/lazada.jpeg')
        file = [('image',
                 ('lazada.jpeg', open('customaddons/intergrate_lazada/static/img/lazada.jpeg', 'rb'), 'image/jpeg'))]
        response = self.env['integrate.lazada']._post_request_data(api, files=file)
        if response.get("code") == "0":
            return response['data']['image']['url']

    def parameters_product(self, rec):
        # Variant custom of product lazada
        attribute_template = rec.attribute_line_ids
        product_variant_ids = rec.product_variant_ids
        variations = {}
        skus = []
        if attribute_template:
            for rec_attribute in range(len(attribute_template)):
                variations.update({
                    "variation%s" % (rec_attribute + 1): {
                        "name": attribute_template[rec_attribute].display_name,
                        "hasImage": "True",
                        "customize": "True",
                        "options": {
                            "option": attribute_template[rec_attribute].value_ids.mapped("name")
                        }
                    }
                })
            if "variation2" in variations:
                variations['variation2'].update({
                    "hasImage": "False",
                })
        for r_variation in product_variant_ids:
            value_attribute = r_variation.product_template_attribute_value_ids

            saleProp = {}
            for r_attribute in range(len(attribute_template)):
                saleProp.update({
                    attribute_template[r_attribute].display_name: value_attribute[r_attribute].name
                })
            sku = {
                "SellerSku": r_variation.default_code,
                "quantity": str(rec.product_variant_ids.stock_quant_ids.filtered(
                    lambda r: r.location_id.warehouse_id.is_warehouse_default == True).quantity),
                "price": str(r_variation.lst_price),
                "package_height": str(r_variation.package_height),
                "package_length": str(r_variation.package_length),
                "package_width": str(r_variation.package_width),
                "package_weight": str(r_variation.package_weight),
            }
            if saleProp:
                sku.update({
                    "saleProp": saleProp
                })
            skus.append(sku)
        parameters = {"payload": {
            "Request": {
                "Product": {
                    "PrimaryCategory": rec.categ_id.category_lazada_id,
                    "Images": {
                        "Image": [
                            self.env['product.template'].upload_image_lazada(rec.image_1920)
                        ]
                    },
                    "Attributes": {
                        "name": rec.name,
                        "description": str(rec.description),
                        "warranty_type": rec.warranty_type,
                        "delivery_option_sof": rec.is_shipped_by_seller
                    },
                    "Skus": {
                        "Sku": skus
                    }
                }
            }
        }}
        if not rec.brand_id:
            parameters['payload']['Request']['Product']['Attributes'].update({"brand": "No Brand"})
        else:
            parameters['payload']['Request']['Product']['Attributes'].update({"brand": rec.brand_id.name})

        if variations:
            parameters["payload"]['Request']['Product'].update({
                "variation": variations
            })
        return parameters

    def cron_job_sync_product_lazada(self):
        api = "/product/create"
        product_push_tiktok = self.env['product.template'].search(
            [('is_push_lazada', '=', True), ('check_sync_product', '=', False)])
        for rec in product_push_tiktok:
            parameters = self.env['product.template'].parameters_product(rec)
            response = self.env['integrate.lazada']._post_request_data(api, parameters)
            if response['code'] == "0":
                rec.check_sync_product = True

    def btn_update_product_lazada(self):
        api = "/product/update"
        for rec in self:
            parameters = self.parameters_product(rec)
            response = self.env['integrate.lazada']._post_request_data(api, parameters)
            if response['code'] == '0':
                notification = {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': ('Cập nhật sản phẩm'),
                        'message': 'Đã cập nhật sản phẩm Lazada',
                        'type': 'success',  # types: success,warning,danger,info
                        'sticky': True,  # True/False will display for few seconds if false
                    },
                }
                return notification

    def cron_job_sync_stock_lazada(self):
        api = '/product/stock/sellable/update'
        search_product_id_lazada = self.env['product.template'].search([('is_push_lazada', '=', True)])
        sku = []
        for product_template_id in search_product_id_lazada:
            for product_variant_id in product_template_id.product_variant_ids:
                stock_quant_ids = product_variant_id.stock_quant_ids.filtered(
                    lambda r: r.location_id.warehouse_id.is_push_lazada == True)
                value = {
                    "SellerSku": product_variant_id.default_code,
                    "Quantity": stock_quant_ids.quantity
                }
                if product_variant_id.is_merge_product == True:
                    product_ids = product_variant_id.search([('marketplace_sku', '=like', product_variant_id.marketplace_sku)])
                    quantity = product_ids.stock_quant_ids.filtered(
                        lambda r: r.location_id.warehouse_id.is_push_lazada == True).mapped("quantity")
                    value.update({"Quantity": sum(quantity)})
                    value.update({"SellerSku": product_variant_id.marketplace_sku})
                sku.append(value)
        parameters = {"payload":
                    {
                        "Request": {
                            "Product": {
                                "Skus": {
                                    "Sku": sku
                                }
                            }
                        }
                    }
                }
        response = self.env['integrate.lazada']._post_request_data(api, parameters)
        if response['code'] == '0':
            if response.get('detail'):
                for r in response.get('detail'):
                    if r.get('seller_sku'):
                        seller_sku = r.get('seller_sku').strip('SellerSku_')
                        product_id = self.env['product.product'].search([('default_code', '=', seller_sku)], limit=1)






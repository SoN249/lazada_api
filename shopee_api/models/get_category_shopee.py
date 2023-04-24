from odoo import fields, models
import json

class CategoryShopee(models.Model):
    _inherit = "product.template"

    category_shopee_id = fields.Integer(string="Id Category")


    def get_category(self):
        api = "/api/orders/search"
        param = {"language": "vi"}
        response = self.env["integrate.shopee"]._post_data_tiktok(api, param)
        data = json.loads(response)
        return data['response']

    def sync_category(self):
        categ_list = self.get_category()
        print(categ_list)
        # for item in categ_list['category_list']:
        #     if item['has_children'] == False:
        #         self.env['product.category'].sudo().create({
        #             "name": item['display_category_name'],
        #             "category_shopee_id": item['category_id']
        #         })
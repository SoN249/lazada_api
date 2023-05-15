from odoo import fields, models

class CategoryShopee(models.Model):
    _inherit = "product.category"

    category_shopee_id = fields.Integer(string="Id Category")
    parent_categ_shopee_id = fields.Integer(string="Parent Category")
    has_children = fields.Boolean("Has children")

    def get_category(self):
        api = "/api/v2/product/get_category"
        param = {"language": "vi"}
        data = self.env["integrate.shopee"]._get_data_shopee(api, payload=None, files=None, param=param, headers=None)
        return data['response']

    def sync_category(self):
        categ_list = self.get_category()
        for item in categ_list['category_list']:
            if item and item['category_id'] not in self.search([]).mapped('category_shopee_id'):
                value = {
                        "name": item['display_category_name'],
                        "category_shopee_id": item['category_id'],
                        "parent_categ_shopee_id": item['parent_category_id'],
                        "has_children": item['has_children']
                }
                self.env['product.category'].sudo().create(value)
        categ_ids = self.search([("parent_categ_shopee_id",'!=', 0)])
        for categ_id in categ_ids:
            parent_id = self.search([("category_shopee_id",'=', categ_id.parent_categ_shopee_id)]).id
            categ_id.sudo().write({
                "parent_id": parent_id
            })

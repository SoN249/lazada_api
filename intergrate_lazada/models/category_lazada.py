from odoo import fields, models


class CategoryLazada(models.Model):
    _inherit = 'product.category'

    category_lazada_id = fields.Integer(string="Id Category")
    leaf = fields.Boolean(string="Leaf")

    def get_category_lazada(self):
        api = "/category/tree/get"
        parameters = {"language_code": "vi_VN"}
        response = self.env['integrate.lazada']._get_request_data(api, parameters)
        categ_id = self.search([("category_lazada_id", "!=", False)]).mapped("category_lazada_id")
        for child in response['data']:
            if child['category_id'] not in categ_id:
                categ_child = self.env['product.category'].sudo().create({
                    "name": child['name'],
                    "category_lazada_id": child['category_id'],
                    "leaf": child['leaf']
                })
                if 'children' in child:
                    for child2 in child['children']:
                        if 'name' in child2 and child2['category_id'] not in categ_id:
                            categ_child2 = self.env['product.category'].sudo().create({
                                "name": child2['name'],
                                "category_lazada_id": child2['category_id'],
                                "leaf": child2['leaf'],
                                "parent_id": categ_child.id
                            })
                            if 'children' in child2:
                                for child3 in child2['children']:
                                    if 'name' in child3 and child3['category_id'] not in categ_id:
                                        categ_child3 = self.env['product.category'].sudo().create({
                                            "name": child3['name'],
                                            "category_lazada_id": child3['category_id'],
                                            "leaf": child3['leaf'],
                                            "parent_id": categ_child2.id
                                        })

                                        if 'children' in child3:
                                            for child4 in child3['children']:
                                                if 'name' in child4 and child4['category_id'] not in categ_id:
                                                    categ_child4 = self.env['product.category'].sudo().create({
                                                        "name": child4['name'],
                                                        "category_lazada_id": child4['category_id'],
                                                        "leaf": child4['leaf'],
                                                        "parent_id": categ_child3.id
                                                    })
                                                    if 'children' in child4:
                                                        for child5 in child4['children']:
                                                            if 'name' in child5 and child5[
                                                                'category_id'] not in categ_id:
                                                                categ_child5 = self.env[
                                                                    'product.category'].sudo().create({
                                                                    "name": child5['name'],
                                                                    "category_lazada_id": child5['category_id'],
                                                                    "leaf": child5['leaf'],
                                                                    "parent_id": categ_child4.id
                                                                })
                                                                if 'children' in child5:
                                                                    for child6 in child5['children']:
                                                                        if 'name' in child6 and child6[
                                                                            'category_id'] not in categ_id:
                                                                            categ_child6 = self.env[
                                                                                'product.category'].sudo().create({
                                                                                "name": child6['name'],
                                                                                "category_lazada_id": child6[
                                                                                    'category_id'],
                                                                                "leaf": child6['leaf'],
                                                                                "parent_id": categ_child5.id
                                                                            })
                                                                            if 'children' in child6:
                                                                                for last_child in child6['children']:
                                                                                    if 'name' in last_child and last_child[
                                                                                        'category_id'] not in categ_id:
                                                                                            self.env[
                                                                                            'product.category'].sudo().create(
                                                                                            {
                                                                                                "name": last_child['name'],
                                                                                                "category_lazada_id":
                                                                                                    last_child[
                                                                                                        'category_id'],
                                                                                                "leaf": last_child['leaf'],
                                                                                                "parent_id": categ_child6.id
                                                                                            })


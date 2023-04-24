from odoo import fields, models

class CategoryLazada(models.Model):
    _inherit = 'product.category'

    category_lazada_id = fields.Integer(string="Id Category")
    leaf = fields.Boolean(string="Leaf")
    def category_lazada(self):
        api = "/category/tree/get"
        parameters ={"language_code": "vi_VN"}
        response = self.env['integrate.lazada']._get_request_data(api, parameters)
        list_child = []
        list_child2 = []
        list_child3 = []
        list_child4 = []
        for child in response['data']:
            if 'children' in child:
                for x in child['children']:
                    list_child.append(x)
            if child['leaf'] == True:
                self.env['product.category'].sudo().create({
                    "name": child['name'],
                    "category_lazada_id": child['category_id'],
                    "leaf": child['leaf']
                })
        for child2 in list_child:
            if 'name' in child2 and child2['leaf'] == True:
                self.env['product.category'].sudo().create({
                        "name": child2['name'],
                        "category_lazada_id": child2['category_id'],
                        "leaf": child2['leaf']
                    })
            elif 'children' in child2:
                for x in child2['children']:
                    list_child2.append(x)

        for child3 in list_child2:
            if 'name' in child3 and child3['leaf'] == True:
                self.env['product.category'].sudo().create({
                        "name": child3['name'],
                        "category_lazada_id": child3['category_id'],
                        "leaf": child3['leaf']
                    })
            elif 'children' in child3:
                for x in child3['children']:
                    list_child3.append(x)

        for child4 in list_child3:
            if 'name' in child4 and child4['leaf'] == True:
                self.env['product.category'].sudo().create({
                    "name": child4['name'],
                    "category_lazada_id": child4['category_id'],
                    "leaf": child4['leaf']
                })
            elif 'children' in child4:
                for x in child4['children']:
                    list_child4.append(x)

        for lstchild in list_child4:
            if 'name' in lstchild and lstchild['leaf'] == True:
                self.env['product.category'].sudo().create({
                    "name": lstchild['name'],
                    "category_lazada_id": lstchild['category_id'],
                    "leaf": lstchild['leaf']
                })
            elif 'children' in lstchild:
                for value in lstchild['children']:
                    self.env['product.category'].sudo().create({
                        "name": value['name'],
                        "category_lazada_id": value['category_id'],
                        "leaf": value['leaf']
                    })


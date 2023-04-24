from odoo import fields, models



class BrandsLazada(models.Model):
    _name= "brands.lazada"

    name = fields.Char("Tên thương hiệu")
    brand_id_lazada = fields.Integer("Brand Id")

    def get_brands_lazada(self):
        api = "/category/brands/query"
        parameters = {
            "startRow": 0,
            "pageSize": 1000,
            "language_code": "vi_VN"}
        response = self.env['integrate.lazada']._get_request_data(api, parameters)
        data = response['data']['module']
        for value in data:
            self.sudo().create({
                "name": value['name'],
                "brand_id_lazada": value['brand_id'],
            })
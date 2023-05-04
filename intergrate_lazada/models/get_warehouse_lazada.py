from odoo import fields, models


class WarehouseLazada(models.Model):
    _inherit = "stock.warehouse"

    is_warehouse_default = fields.Boolean("Is lazada warehouse default")
    warehouse_lazada_code= fields.Char("Warehouse Lazada")


    def get_warehouse_lazada(self):
        api = "/rc/warehouse/get"
        response = self.env['integrate.lazada']._get_request_data(api, parameters = None)
        return response['result']
    def set_default_warehouse(self):
        api = "/rc/warehouse/detail/get"
        response = self.env['integrate.lazada']._get_request_data(api, parameters=None)
        return response['result']
    def sync_warehouse(self):
        warehouse_id = self.get_warehouse_lazada()
        for warehouse in warehouse_id['module']:
            partner_value = {
                "name": warehouse['name'],
                "is_company": "True",
                "street": warehouse['detailAddress']
            }
            if warehouse['code'] not in self.sudo().search([]).mapped("warehouse_lazada_code"):
                res = self.env['res.partner'].sudo().create(partner_value)
                values = {
                    "name": warehouse['name'],
                    "warehouse_lazada_code": warehouse['code'],
                    "partner_id": res.id,
                    "code": warehouse['code'][-5:]
                }
                warehouse_id = self.sudo().create(values)
                warehouse_id.view_location.write({"name": warehouse['name']})
                default_id = self.set_default_warehouse()
                if warehouse['code'] in default_id['module']['warehouse_code']:
                    warehouse_id.is_warehouse_default = True





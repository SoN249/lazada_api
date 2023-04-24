from odoo import fields, models


class SStockPickings(models.Model):
    _inherit = "stock.picking"

    status = fields.Selection([("ready_to","Hoàn tất đóng gói"),
                               ("delivered","Giao hàng thành công")
                               ], string="Trạng thái giao hàng")


    def get_order_trace(self, order_id):
        api= "/logistic/order/trace"
        parameters = {
            "order_id": order_id
           }
        response = self.env['integrate.lazada']._get_request_data(api, parameters)
        return response['result']

    def sync_package(self):
        order_id = self.env['sale.order'].sudo().search([]).filtered(lambda order: order.lazada_order_id == True)
        print(order_id)

from odoo import fields, models
import json
import urllib3
import datetime as date
from datetime import datetime
urllib3.disable_warnings()
class SOrderTiktok(models.Model):
    _inherit = "sale.order"

    lazada_order_id = fields.Char("Lazada ID")
    is_lazada_order = fields.Boolean("Đơn hàng Lazada")
    order_status = fields.Selection([("unpaid","Unpaid"),
                               ("pending","Pending"),
                               ("packed","Packed"),
                               ("ready_to_ship", "Ready to Ship"),
                               ("delivered", "Delivered"),
                               ("canceled", "Canceled"),
                               ("returned", "Returned"),
                               ], string="Trạng thái đơn hàng")
    shipping_provider_type = fields.Selection([('express', "EXPRESS"),
                                               ("standard", "STANDARD"),
                                               ("economy","ECONOMY"),
                                               ("instant", "INSTANT"),
                                               ("seller_own_fleet", "SELLER OWN FLEET"),
                                               ("pickup_in_store", "PICKUP IN STORE"),
                                               ("digital", "DIGITAL")
                                               ], string="Phương thức vận chuyển")
    shipping_allocate_type = fields.Char("shipping_allocate_type")

    # Get data of order lazada
    def get_order_list(self, offset):
        api = "/orders/get"
        previous_date = date.datetime.now() - date.timedelta(days=1)
        next_date = date.datetime.now() + date.timedelta(days=1)
        parameters = {
            "sort_direction": "DESC",
            "offset": offset,
            "limit": 100,
            "sort_by": "created_at",
            "created_after": previous_date.strftime("%Y-%m-%dT00:00:00+07:00"),
            "created_before":  next_date.strftime("%Y-%m-%dT00:00:00+07:00")
        }

        response = self.env['integrate.lazada']._get_request_data(api, parameters)
        return response['data']

    # Get data product of order lazada
    def get_order_item(self, order_id):
        api = '/order/items/get'
        parameters = {
            "order_id": order_id
        }
        response = self.env['integrate.lazada']._get_request_data(api, parameters)
        return response['data']

    # get data shipment provider then confirm order
    def get_shipment_provider(self, order_id, order_items):
        api = "/order/shipment/providers/get"
        parameters = {
            "getShipmentProvidersReq":
                {"orders": [
            {"order_id": order_id,
             "order_item_ids": order_items}
        ]}
        }
        response = self.env['integrate.lazada']._post_request_data(api, parameters)
        return response['result']

    #set order status packed
    def set_pack_order(self, order_items, type):
        api = "/order/pack"
        parameters = {
                "shipping_provider": type,
                "delivery_type": 'dropship',
                "order_item_ids": str(order_items)
        }
        res = self.env['integrate.lazada']._post_request_data(api, parameters)
        return res


    def action_confirm(self):
        if self.order_status in ['ready_to_ship','delivered','canceled','returned']:
            return super(SOrderTiktok, self).action_confirm()

    def sync_order_lazada(self):
        offset = 0
        orders = []
        while True:
            order_list = self.get_order_list(offset)
            for order in order_list['orders']:
                orders.append(order['order_id'])
                order_item = self.get_order_item(order['order_id'])
                warehouse_id = self.env["stock.warehouse"].sudo().search(
                    [("warehouse_lazada_code", 'ilike', order['warehouse_code'])])
                date_order = datetime.strptime(order["created_at"][:-6], '%Y-%m-%d %H:%M:%S') - date.timedelta(hours=7)
                values= {
                    "partner_id": 24,
                    "pricelist_id": 1,
                    "partner_invoice_id": 24,
                    "partner_shipping_id": 24,
                    "lazada_order_id": order['order_id'],
                    "is_lazada_order": True,
                    "order_status": order['statuses'][0],
                    "warehouse_id": warehouse_id.id,
                    "currency_id": self.pricelist_id.currency_id.id,
                    "date_order":date_order,
                    "shipping_provider_type": order_item[0]["shipping_provider_type"]
                }
                if str(order['order_id']) not in self.search([]).mapped("lazada_order_id"):
                    order = self.create(values)
                    for item in order_item:
                        product_id = self.env['product.product'].sudo().search([('default_code','=like', item['sku'])])
                        if product_id:
                            value_product = {
                                    "order_id": order.id,
                                    "product_id": product_id.id,
                                    "order_item_id":item['order_item_id']
                            }
                            order.order_line.sudo().create([value_product])
                    order.action_confirm()
            if len(orders) == 100:
                orders.clear()
                offset += 100
            else:
                orders.clear()
                break

    def update_order(self):
        api = "/order/get"
        order_id = self.env['sale.order'].search([("is_lazada_order",'=', True),("order_status",'not in',['delivered','canceled'])])
        for id in order_id:
            parameters = {
                "order_id": id.lazada_order_id
            }
            response = self.env['integrate.lazada']._get_request_data(api, parameters)
            id.action_confirm()
            id.write({"order_status": response['data']['statuses'][-1]})







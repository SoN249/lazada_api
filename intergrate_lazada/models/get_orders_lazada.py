from odoo import fields, models
import json
import urllib3
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
                               ("delived", "Delived"),
                               ("canceled", "Canceled"),
                               ("returned", "Returned"),
                               ], string="Trạng thái đơn hàng")
    shipping_provider_type = fields.Selection([('EXPRESS', "EXPRESS"),
                                               ("STANDARD", "STANDARD"),
                                               ("ECONOMY","ECONOMY"),
                                               ("INSTANT", "INSTANT"),
                                               ("SELLER_OWN_FLEET", "SELLER OWN FLEET"),
                                               ("PICKUP_IN_STORE", "PICKUP IN STORE"),
                                               ("DIGITAL", "DIGITAL")
                                               ], string="Phương thức vận chuyển")
    def get_order_list(self, offset):
        api = "/orders/get"
        now = datetime.now()
        date_time_str = now.strftime("%Y-%m-%dT00:00:00+07:00")
        parameters = {
            "sort_direction": "DESC",
            "offset": offset,
            "limit": 50,
            "sort_by": "created_at",
            "created_after":date_time_str
        }

        response = self.env['integrate.lazada']._get_request_data(api, parameters)
        return response['data']

    def get_order_item(self, order_id):
        api = '/order/items/get'
        parameters = {
            "order_id": order_id
        }
        response = self.env['integrate.lazada']._get_request_data(api, parameters)
        return response['data']

    def sync_order_lazada(self):
        offset = 0
        orders = []
        order_list = self.get_order_list(offset)

        for order in order_list['orders']:
            orders.append(order['order_id'])
            order_item = self.get_order_item(order['order_id'])
            warehouse_id = self.env["stock.warehouse"].sudo().search(
                [("warehouse_lazada_code", 'ilike', order['warehouse_code'])])
            customer_billing = self.env["res.partner"].sudo().create({
                "name": "TMĐT-"+ order['address_billing']['first_name']
            })
            customer_shipping = self.env["res.partner"].sudo().create({
                "name": "TMĐT-"+ order['address_shipping']['first_name'],
                "parent_id": customer_billing.id
            })
            values= {
                "partner_id": customer_billing.id,
                "pricelist_id": '1',
                "partner_invoice_id": customer_billing.id,
                "partner_shipping_id": customer_shipping.id,
                "lazada_order_id": order['order_id'],
                "is_lazada_order": True,
                "order_status": order['statuses'][0],
                "warehouse_id": warehouse_id.id,
            }
            order = self.create(values)
            order.sudo().search([]).write({"currency_id": 23})

            for i in order_item:
                product_id = self.env['product.product'].sudo().search([('default_code','=like', i['sku'])])
                value_product = {
                        "order_id": order.id,
                        "product_id": product_id.id,
                        "product_uom_qty": product_id.qty_available
                }
                order.order_line.sudo().create([value_product])


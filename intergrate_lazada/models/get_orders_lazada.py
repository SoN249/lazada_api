from odoo import fields, models,_
from odoo.exceptions import ValidationError
import urllib3
import datetime as date
from datetime import datetime
from odoo.tests import Form

urllib3.disable_warnings()


class SOrderTiktok(models.Model):
    _inherit = "sale.order"

    lazada_order_id = fields.Char("Lazada ID")
    is_lazada_order = fields.Boolean("Đơn hàng Lazada")
    order_status = fields.Selection([("unpaid", "Unpaid"),
                                     ("pending", "Pending"),
                                     ("packed", "Packed"),
                                     ("ready_to_ship", "Ready to Ship"),
                                     ("shipped", "Shipped"),
                                     ("delivered", "Delivered"),
                                     ("canceled", "Canceled"),
                                     ("returned", "Returned"),
                                     ('repacked', "Repacked")
                                     ], string="Trạng thái đơn hàng")
    shipping_provider_type = fields.Selection([('express', "EXPRESS"),
                                               ("standard", "STANDARD"),
                                               ("economy", "ECONOMY"),
                                               ("instant", "INSTANT"),
                                               ("seller_own_fleet", "SELLER OWN FLEET"),
                                               ("pickup_in_store", "PICKUP IN STORE"),
                                               ("digital", "DIGITAL")
                                               ], string="Phương thức vận chuyển")
    shipping_allocate_type = fields.Char("shipping_allocate_type")
    tracking_number = fields.Char('Tracking Number')

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
            "created_before": next_date.strftime("%Y-%m-%dT00:00:00+07:00")
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

    def sync_order_lazada(self):
        offset = 0
        order_ids = []
        while True:
            order_list = self.get_order_list(offset)
            for order in order_list['orders']:
                order_ids.append(order['order_id'])
                order_item = self.get_order_item(order['order_id'])
                warehouse_id = self.env["stock.warehouse"].sudo().search(
                    [("is_push_lazada", '=', True)])
                date_order = datetime.strptime(order["created_at"][:-6], '%Y-%m-%d %H:%M:%S') - date.timedelta(hours=7)
                customer_lazada = self.env["res.partner"].search([('name', '=', "TMĐT- customer- lazada")], limit=1)
                values = {
                    "partner_id": customer_lazada.id,
                    "pricelist_id": 1,
                    "partner_invoice_id": customer_lazada.id,
                    "partner_shipping_id": customer_lazada.id,
                    "lazada_order_id": order['order_id'],
                    "is_lazada_order": True,
                    "order_status": order['statuses'][0],
                    "warehouse_id": warehouse_id.id,
                    "currency_id": self.pricelist_id.currency_id.id,
                    "date_order": date_order,
                    "shipping_provider_type": order_item[0]["shipping_provider_type"]
                }
                if str(order['order_id']) not in self.search([]).mapped("lazada_order_id"):
                    order = self.create(values)
                    for item in order_item:
                        product_ids_sku = self.env['product.product'].sudo().search([('default_code', '=like', item['sku'])])
                        product_ids_msku = self.env['product.product'].sudo().search([('marketplace_sku', '=like', item['sku'])])
                        value_product = {}
                        if product_ids_sku:
                            value_product.update({
                                "order_id": order.id,
                                "product_id": product_ids_sku.id,
                                "order_item_id": item['order_item_id']
                            })
                        elif product_ids_msku:
                            for product_id in product_ids_msku:
                                if id.stock_quant_ids.filtered(lambda r: r.location_id.warehouse_id.is_push_lazada == True).quantity != 0:
                                    value_product.update({
                                        "order_id": order.id,
                                        "product_id": product_id.id,
                                        "order_item_id": item['order_item_id']
                                    })

                        if product_ids_sku or product_ids_msku:
                            order.order_line.sudo().create([value_product])
                        order.action_confirm()
                    if order.order_status == 'canceled':
                        order.action_cancel()

            if len(order_ids) == 100:
                order_ids.clear()
                offset += 100
            else:
                order_ids.clear()
                break

    def update_order(self):
        api = "/order/get"
        order_ids = self.env['sale.order'].search(
            [("is_lazada_order", '=', True), ("order_status", 'not in', ['delivered'])])
        for order_id in order_ids:
            parameters = {
                "order_id": order_id.lazada_order_id
            }
            response = self.env['integrate.lazada']._get_request_data(api, parameters)
            order_id.write({"order_status": response['data']['statuses'][-1]})
            if order_id.order_status == 'canceled':
                order_id.action_cancel()
    def btn_update_customer(self):
            view = self.env.ref('intergrate_lazada.infor_customer_form_view')
            return {
                'name': _('Choose customer for order'),
                'type': 'ir.actions.act_window',
                'res_model': 'infor.customer',
                'views': [(view.id, 'form')],
                'target': 'new',
            }


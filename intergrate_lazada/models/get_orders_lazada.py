from odoo import fields, models, _, api
import datetime as date
from datetime import datetime

class SOrderTiktok(models.Model):
    _inherit = "sale.order"

    lazada_order_id = fields.Char("Lazada ID")
    is_lazada_order = fields.Boolean("Đơn hàng Lazada")
    marketplace_order_status = fields.Selection([("unpaid", "Chưa thanh toán"),
                                                 ("pending", "Chờ xử lý"),
                                                 ("packed", "Đã đóng gói"),
                                                 ("ready_to_ship", "Sẵn sàng giao"),
                                                 ("shipped", "Đang giao hàng"),
                                                 ("delivered", "Đã giao hàng"),
                                                 ("canceled", "Đã hủy"),
                                                 ("returned", "Đơn hàng hoàn trả"),
                                                 ('repacked', "Đóng gói lại")
                                                 ], string="Trạng thái đơn hàng")

    shipping_provider_type = fields.Selection([('express', "EXPRESS"),
                                               ("standard", "STANDARD"),
                                               ("economy", "ECONOMY"),
                                               ("instant", "INSTANT"),
                                               ("seller_own_fleet", "SELLER OWN FLEET"),
                                               ("pickup_in_store", "PICKUP IN STORE"),
                                               ("digital", "DIGITAL")
                                               ], string="Phương thức vận chuyển")


    # Get data of order lazada
    def get_order_list(self, offset):
        api = "/orders/get"
        previous_date = date.datetime.now() - date.timedelta(days=7)
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
        if response:
             return response['data']

    # Get data product of order lazada
    def get_order_item(self, order_id):
        api = '/order/items/get'
        parameters = {
            "order_id": order_id
        }
        response = self.env['integrate.lazada']._get_request_data(api, parameters)
        if response:
            return response['data']

    def sync_order_lazada(self):
        offset = 0
        order_ids = []
        while True:
            order_list = self.get_order_list(offset)
            if order_list:
                for order_id in order_list['orders']:
                    order_ids.append(order_id['order_id'])
                    if str(order_id['order_id']) not in self.search([("is_lazada_order", '=', True)]).mapped(
                            "lazada_order_id"):
                        order_item = self.get_order_item(order_id['order_id'])
                        warehouse_id = self.env["stock.warehouse"].sudo().search(
                            [("is_push_lazada", '=', True)])
                        date_order = datetime.strptime(order_id["created_at"][:-6], '%Y-%m-%d %H:%M:%S') - date.timedelta(
                            hours=7)
                        customer_lazada = self.env["res.partner"].search([('name', '=', "TMĐT-customer-lazada")], limit=1)
                        source_id = self.env["utm.source"].search([('name', '=', "Lazada")], limit=1)
                        values = {
                            "partner_id": customer_lazada.id,
                            "partner_invoice_id": customer_lazada.id,
                            "partner_shipping_id": customer_lazada.id,
                            "lazada_order_id": order_id['order_id'],
                            "is_lazada_order": True,
                            "marketplace_order_status": order_id['statuses'][0],
                            "warehouse_id": warehouse_id.id,
                            "date_order": date_order,
                            "shipping_provider_type": order_item[0]["shipping_provider_type"],
                            "state": 'sale',
                            "source_id": source_id.id
                        }
                        order = self.create(values)
                        for item in order_item:
                            product_ids = self.env['product.product'].sudo().search(
                                ['|',('default_code', '=', item['sku']),('marketplace_sku', '=', item['sku'])], order='id DESC')
                            if product_ids:
                                value_product = {}
                                for product_id in product_ids:
                                    if product_id.stock_quant_ids.filtered(
                                            lambda r: r.location_id.warehouse_id.is_push_lazada == True).quantity != 0 :
                                            value_product.update({
                                                "order_id": order.id,
                                                "product_id": product_id.id
                                            })
                                order.order_line.sudo().create([value_product])

                if len(order_ids) == 100:
                    order_ids.clear()
                    offset += 100
                else:
                    order_ids.clear()
                    break


    # def sync_order_status(self):
    #     api = "/order/get"
    #     order_ids = self.env['sale.order'].search(
    #         [("is_lazada_order", '=', True)])
    #     for order_id in order_ids:
    #         if order_id.marketplace_order_status not in ['delivered', 'canceled']:
    #             parameters = {
    #                 "order_id": order_id.lazada_order_id
    #             }
    #             response = self.env['integrate.lazada']._get_request_data(api, parameters)
    #             if response:
    #                 order_id.write({"marketplace_order_status": response['data']['statuses'][-1]})
    #         if order_id.marketplace_order_status not in ['unpaid','pending','packed']:
    #             for picking_id in order_id.picking_ids:
    #                 if picking_id.is_do_return == False and picking_id.state == 'assigned':
    #                     picking_id.action_set_quantities_to_reservation()
    #                     picking_id.button_validate()
    #                     if order_id.marketplace_order_status == 'canceled':
    #                         return_picking_id = self.env['stock.return.picking'].create({'picking_id': picking_id.id})
    #                         return_picking_id.sudo()._onchange_picking_id()
    #                         if len(return_picking_id.product_return_moves) > 0 and sum(
    #                                 return_picking_id.product_return_moves.mapped('quantity')) > 0:
    #                             result_return_picking = return_picking_id.sudo().create_returns()
    #                             if result_return_picking:
    #                                 do_return = self.env['stock.picking'].search(
    #                                     [('id', '=', result_return_picking.get('res_id'))])
    #                                 do_return.write({'is_do_return': True})

    def btn_update_customer(self):
        view = self.env.ref('intergrate_lazada.infor_customer_form_view')
        return {
            'name': _('Choose customer for order'),
            'type': 'ir.actions.act_window',
            'res_model': 'infor.customer',
            'views': [(view.id, 'form')],
            'target': 'new',
        }

from odoo import http
from odoo.http import request
import json
from odoo import SUPERUSER_ID

class OrderStatusWebhook(http.Controller):
    @http.route('/order_status', type='json', auth='none', methods=['POST'],
                csrf=False)
    def get_webhook_url(self, *args, **kwargs):
        data = json.loads(request.httprequest.data)
        print(data)
        if data:
            if 'fulfillment_package_id' not in data['data'] and 'order_status' in data['data']:
                order_id = request.env['sale.order'].sudo().search(
                    [('is_lazada_order', '=', True), ('lazada_order_id', '=', data['data']['trade_order_id'])])
                if order_id.marketplace_order_status != data['data']['order_status']:
                    order_id.marketplace_order_status = data['data']['order_status']
                    request.env['sale.order'].with_user(SUPERUSER_ID).sudo()._compute_return_stock_picking_lazada(order_id)
            elif 'fulfillment_package_id' in data['data'] and 'status' in data['data']:
                order_id_shipment = request.env['sale.order'].sudo().search(
                    [('is_lazada_order', '=', True), ('lazada_order_id', '=', data['data']['trade_order_id'])])
                picking_ids = order_id_shipment.picking_ids
                if picking_ids:
                    for picking_id in picking_ids:
                        if picking_id.is_do_return == False:
                            picking_id.sudo().status = data['data']['status']

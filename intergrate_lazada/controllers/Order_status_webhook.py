from odoo import http
from odoo.http import request
import json
from odoo import SUPERUSER_ID

class OrderStatusWebhook(http.Controller):
    @http.route('/lzd_webhook', type='json', auth='none', methods=['POST'],
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
                    picking_ids = order_id.picking_ids
                    if picking_ids:
                        for picking_id in picking_ids:
                            if order_id.marketplace_order_status == 'read_to_ship':
                                picking_id.action_set_quantities_to_reservation()
                                picking_id.button_validate()
                            if picking_id.is_do_return == False and order_id.marketplace_order_status == 'canceled':
                                return_picking_id = request.env['stock.return.picking'].with_user(SUPERUSER_ID).sudo().create(
                                    {'picking_id': picking_id.id})
                                return_picking_id.sudo()._onchange_picking_id()
                                if len(return_picking_id.product_return_moves) > 0 and sum(
                                        return_picking_id.product_return_moves.mapped('quantity')) > 0:
                                    result_return_picking = return_picking_id.sudo().create_returns()
                                    if result_return_picking:
                                        do_return = request.env['stock.picking'].sudo().search(
                                            [('id', '=', result_return_picking.get('res_id'))])
                                        do_return.write({'is_do_return': True})
            elif 'fulfillment_package_id' in data['data'] and 'status' in data['data']:
                order_id_shipment = request.env['sale.order'].sudo().search(
                    [('is_lazada_order', '=', True), ('lazada_order_id', '=', data['data']['trade_order_id'])])
                picking_ids = order_id_shipment.picking_ids
                if picking_ids:
                    for picking_id in picking_ids:
                        if picking_id.is_do_return == False:
                            picking_id.sudo().status = data['data']['status']

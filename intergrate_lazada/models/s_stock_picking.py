from odoo import fields, models, _
from odoo.exceptions import ValidationError


class SStockPickings(models.Model):
    _inherit = "stock.picking"

    status = fields.Selection([("ready_to", "Hoàn tất đóng gói"),
                               ("ship_info", "Tìm được người giao hàng"),
                               ("delivered", "Giao hàng thành công")
                               ], string="Trạng thái giao hàng")
    package_id = fields.Char("Package Id Lazada")
    is_do_return = fields.Boolean("Is DO return")

    def get_order_trace(self, order_id):
        api = "/logistic/order/trace"
        parameters = {
            "order_id": order_id
        }
        response = self.env['integrate.lazada']._get_request_data(api, parameters)
        if response['code'] == '0' and 'module' in response['result']:
            return response['result']['module']

    def sync_shipment(self):
        order_ids = self.env['sale.order'].sudo().search(
            [("is_lazada_order", '=', True), ('marketplace_order_status', 'not in', ['pending', 'packed', 'unpaid'])])
        for order_id in order_ids:
            order_trace = self.get_order_trace(order_id.lazada_order_id)
            if order_trace is not None and len(order_trace[0]['package_detail_info_list']) > 0:
                picking_ids = order_id.picking_ids
                if picking_ids:
                    for picking_id in picking_ids:
                        if picking_id.is_do_return == False and picking_id.status not in ['delivered']:
                            picking_id.sudo().write(
                                {"package_id": order_trace[0]['package_detail_info_list'][0]['ofc_package_id'],
                                 "status":
                                     order_trace[0]['package_detail_info_list'][0]['logistic_detail_info_list'][-1][
                                         'detail_type']})
                            if picking_id.status == "delivered":
                                picking_id.action_set_quantities_to_reservation()
                                picking_id.button_validate()

    def btn_shipping_document(self):
        view = self.env.ref('intergrate_lazada.shipping_document_type_form_view')
        package_id = self.package_id
        if self.sale_id.shipping_provider_type not in ['seller_own_fleet']:
            return {
                'name': _('Choose Type of Shipping document'),
                'type': 'ir.actions.act_window',
                'res_model': 'shipping.document',
                'views': [(view.id, 'form')],
                'target': 'new',
                'context': {'package_id': package_id},
            }
        else:
            raise ValidationError("Đơn hàng vận chuyển bởi người bán không thể in nhãn !")

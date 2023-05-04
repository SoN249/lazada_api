from odoo import fields, models, _


class SStockPickings(models.Model):
    _inherit = "stock.picking"

    status = fields.Selection([("ready_to","Hoàn tất đóng gói"),
                               ("delivered","Giao hàng thành công")
                               ], string="Trạng thái giao hàng")
    package_lazada_id = fields.Char("Package Id Lazada")

    def get_order_trace(self, order_id):
        api= "/logistic/order/trace"
        parameters = {
            "order_id": order_id
           }
        response = self.env['integrate.lazada']._get_request_data(api, parameters)
        if response['code'] == '0':
            return response['result']['module']

    def sync_package(self):
        order_id = self.env['sale.order'].sudo().search([("is_lazada_order",'=', True)])
        for id in order_id:
            # if id.picking_ids and id.picking_ids.state not in ['assigned']:
            #     id.picking_ids.action_assign()
            if id.picking_ids and id.order_status not in ['pending','packed','unpaid']:
                order_trace = self.get_order_trace(id.lazada_order_id)
                package_id = id.picking_ids[-1]
                if package_id:
                    package_id[-1].sudo().write(
                        {"package_lazada_id": order_trace[0]['package_detail_info_list'][0]['ofc_package_id'],
                         "status": order_trace[0]['package_detail_info_list'][0]['logistic_detail_info_list'][0]['detail_type'],
                         "note": order_trace[0]['package_detail_info_list'][0]['logistic_detail_info_list'][0]['description']
                         })


    def btn_shipping_document(self):
            view = self.env.ref('intergrate_lazada.shipping_document_type_form_view')
            package_id = self.package_lazada_id

            return {
                'name': _('Choose Type of Shipping document'),
                'type': 'ir.actions.act_window',
                'res_model': 'shipping.document',
                'views': [(view.id, 'form')],
                'target': 'new',
                'context': {'package_id': package_id},
            }

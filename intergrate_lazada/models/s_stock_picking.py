from odoo import fields, models, _
from odoo.tests import Form

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
        if response['code'] == '0' and 'module' in response:
            return response['result']['module']
    def get_return_order(self, page_no):
        api = '/reverse/getreverseordersforseller'
        parameters ={
            "page_size": 100,
            "page_no": page_no
        }
        response = self.env['integrate.lazada']._get_request_data(api, parameters)
        if response['code'] == '0':
            if len(response['result']['items']) > 0:
                return response['result']['items']
    def sync_package(self):
        order_id = self.env['sale.order'].sudo().search([("is_lazada_order",'=', True),('order_status','not in',['pending','packed','unpaid'])])
        for id in order_id:

            if id.picking_ids and id.order_status not in ['pending','packed','unpaid','canceled']:
                order_trace = self.get_order_trace(id.lazada_order_id)
                package_id = id.picking_ids[-1]
                if package_id:
                    package_id.sudo().write(
                        {"package_lazada_id": order_trace[0]['package_detail_info_list'][0]['ofc_package_id'],
                         "status": order_trace[0]['package_detail_info_list'][0]['logistic_detail_info_list'][0]['detail_type'],
                         "note": order_trace[0]['package_detail_info_list'][0]['logistic_detail_info_list'][0]['description']
                         })
                    if package_id.state == 'assigned':
                        package_id.action_set_quantities_to_reservation()
                        package_id.button_validate()

    def test(self):
        return_form = Form(self.env['stock.return.picking'].with_context(active_id= self.id, active_model='stock.picking'))
        wizard = return_form.save()
        wizard.product_return_moves.write({'product_id':16,'quantity': 1 })
        wizard.create_returns()

    def cronjob_create_return(self):

        page_no = 1
        res = self.get_return_order(page_no)
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

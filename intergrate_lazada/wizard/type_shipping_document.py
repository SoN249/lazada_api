from odoo import fields, models
import json
from odoo.exceptions import ValidationError
class ShippingDocumentType(models.TransientModel):
    _name="shipping.document"

    document_type = fields.Selection([('HTML', "HTML"),
                                      ('PDF', 'PDF'),], required = True, default="PDF")


    def btn_confirm(self):
        package_id = self.env.context.get('package_id')

        api = "/order/package/document/get"
        parameters ={"getDocumentReq":{
                "doc_type": self.document_type,
                 "packages":[
                     {"package_id": package_id}
                 ]}}
        response = self.env['integrate.lazada']._post_request_data(api, parameters)

        if response['code'] == '0':
            url = response['result']['data']['pdf_url']
            return {
                'name': 'Shipping Document',
                'type': 'ir.actions.act_url',
                'url': url,
                'target': 'new',
            }
        else:
            raise  ValidationError("Không có dữ liệu shipping document ")

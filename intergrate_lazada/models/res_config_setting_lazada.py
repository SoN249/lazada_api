from odoo import fields, models
from odoo.exceptions import ValidationError
import time
import requests
import urllib3
import hmac
import hashlib
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ResConfigSettingLazada(models.TransientModel):
    _inherit = "res.config.settings"

    app_key= fields.Char("App key", config_parameter="intergrate_lazada.app_key")
    app_secret = fields.Char("App secret",config_parameter="intergrate_lazada.app_secret")
    auth_code = fields.Char("Auth code", config_parameter="intergrate_lazada.auth_code")
    url = fields.Char("URL", config_parameter="intergrate_lazada.url")

    def btn_get_auth(self):
        if self.app_key:
            url = "https://auth.lazada.com/oauth/authorize?response_type=code&force_auth=true&redirect_uri=https://www.lazada.vn&client_id="+self.app_key
            return {
                'name': 'Authorization',
                'type': 'ir.actions.act_url',
                'url': url,  # Replace this with tracking link
                'target': 'new',  # you can change target to current, self, new.. etc
            }
        else:
            raise ValidationError("Invalid Client ID")


    def btn_access_token(self):

        timestamp = int(round(time.time() * 1000))
        api = "/auth/token/create"
        parameters ={"app_key":self.app_key,"timestamp":timestamp,"code":self.auth_code, "sign_method":"sha256"}
        sort_dict = sorted(parameters)
        parameters_str = "%s%s" % (api, str().join('%s%s' % (key, parameters[key]) for key in sort_dict))
        h = hmac.new(self.app_secret.encode(encoding="utf-8"), parameters_str.encode(encoding="utf-8"), digestmod=hashlib.sha256)
        sign =  h.hexdigest().upper()

        endpoint = "https://auth.lazada.com/rest"
        url = endpoint + api
        payload ={}
        headers ={}
        params = {
            "app_key": self.app_key,
            "sign_method": "sha256",
            "sign": sign,
            "code": self.auth_code,
            "timestamp": timestamp
        }
        res = requests.get(url,
            data=payload,
            params=params,
            headers=headers,
            verify=False)

        res_data = res.json()
        token = self.env['integrate.lazada'].sudo().search([])
            # Token test
        token_test = "50000201909ffjcsqjdca1fa10d14qdMw1cjkxh0mQXjczAssDKp3rNv1AholnGj"
        if not token:
            self.env['integrate.lazada'].sudo().create({"access_token": token_test
                })
        else:
            token.sudo().write({"access_token": token_test})


    def sync_data(self):
        # self.env['product.category'].category_lazada()
        # self.env['brands.lazada'].get_brands_lazada()
        # self.env['stock.warehouse'].sync_warehouse()
        # self.env['sale.order'].sync_order_lazada()
        self.env['stock.picking'].sync_package()

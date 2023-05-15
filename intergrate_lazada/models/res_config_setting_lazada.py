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
    app_key = fields.Char("App key", config_parameter="intergrate_lazada.app_key")
    app_secret = fields.Char("App secret", config_parameter="intergrate_lazada.app_secret")
    auth_code = fields.Char("Auth code", config_parameter="intergrate_lazada.auth_code")
    url = fields.Char("URL", config_parameter="intergrate_lazada.url")
    is_connected_lazada = fields.Boolean("Is connected  Lazada",
                                         config_parameter="intergrate_lazada.is_connected_lazada")

    def btn_get_auth(self):
        if self.app_key:
            url = "https://auth.lazada.com/oauth/authorize?response_type=code&force_auth=true&redirect_uri=https://www.lazada.vn&client_id=" + self.app_key
            return {
                'name': 'Authorization',
                'type': 'ir.actions.act_url',
                'url': url,  # Replace this with tracking link
                'target': 'new',  # you can change target to current, self, new.. etc
            }
        else:
            raise ValidationError("Invalid Client ID")

    def btn_connect_lazada(self):
        timestamp = int(round(time.time() * 1000))
        api = "/auth/token/create"
        parameters = {"app_key": self.app_key, "timestamp": timestamp, "code": self.auth_code, "sign_method": "sha256"}

        sort_dict = sorted(parameters)
        parameters_str = "%s%s" % (api, str().join('%s%s' % (key, parameters[key]) for key in sort_dict))
        h = hmac.new(self.app_secret.encode(encoding="utf-8"), parameters_str.encode(encoding="utf-8"),
                     digestmod=hashlib.sha256)
        sign = h.hexdigest().upper()

        parameters.update({"sign": sign})

        url = "https://auth.lazada.com/rest" + api
        res = requests.get(url,
                           data={},
                           params=parameters,
                           headers={},
                           verify=False)
        res_data = res.json()
        if res_data['code'] == '0':
            ir_config_param_obj = self.env['ir.config_parameter'].sudo()
            ir_config_param_obj.set_param('intergrate_lazada.access_token', res_data['access_token'])
            ir_config_param_obj.set_param('intergrate_lazada.refresh_token', res_data['refresh_token'])
            ir_config_param_obj.set_param('intergrate_lazada.is_connected_lazada', True)
            ir_config_param_obj.set_param('intergrate_lazada.expires_in', res_data['expires_in'])

        else:
            raise ValidationError("Kết nối thất bại")
    def btn_disconnect_lazada(self):
        ir_config_param_obj = self.env['ir.config_parameter'].sudo()
        ir_config_param_obj.set_param('intergrate_lazada.is_connected_lazada', False)
        ir_config_param_obj.search([('key', '=', 'intergrate_lazada.auth_code')]).unlink()
        ir_config_param_obj.search([('key', '=', 'intergrate_lazada.access_token')]).unlink()
        ir_config_param_obj.search([('key', '=', 'intergrate_lazada.refresh_token')]).unlink()
    def cronjob_refresh_token(self):
        api = '/auth/token/refresh'
        endpoint = 'https://auth.lazada.com/rest'
        timestamp = int(round(time.time() * 1000))
        ir_config_param_obj = self.env['ir.config_parameter'].sudo()
        parameters = {"app_key": ir_config_param_obj.get_param('intergrate_lazada.app_key'), "sign_method": "sha256",
                      "timestamp": timestamp, "refresh_token": ir_config_param_obj.get_param('intergrate_lazada.refresh_token')}

        sign = self.env['integrate.lazada'].create_signature(api, parameters)
        parameters.update({'sign': sign})

        url = endpoint + api
        res = requests.get(
            url,
            data={},
            params=parameters,
            verify=False
        )
        res_data = res.json()
        if res_data['code'] == '0':
            ir_config_param_obj = self.env['ir.config_parameter'].sudo()
            ir_config_param_obj.set_param('intergrate_lazada.access_token', res_data['access_token'])
            ir_config_param_obj.set_param('intergrate_lazada.refresh_token', res_data['refresh_token'])
            ir_config_param_obj.set_param('intergrate_lazada.expires_in', res_data['expires_in'])



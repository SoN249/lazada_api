from odoo import fields, models
import requests
import time
import hmac
import hashlib
import json
import urllib.parse


class IntegrateLazada(models.Model):
    _name = 'integrate.lazada'

    access_token = fields.Char(string='Access token')
    parameters = fields.Text("Parameters")

    def create_signature(self, api,params, timestamp):
        ir_config = self.env['ir.config_parameter'].sudo()
        parameters = {"app_key": ir_config.get_param('intergrate_lazada.app_key', ''), "sign_method": "sha256",
                  "access_token": self.sudo().search([]).access_token, "timestamp": timestamp}
        parameters.update(params)
        sort_dict = sorted(parameters)
        secret = ir_config.get_param('intergrate_lazada.app_secret','')
        parameters_str = "%s%s" % (api,str().join('%s%s' % (key, parameters[key]) for key in sort_dict))
        h = hmac.new(secret.encode(encoding="utf-8"), parameters_str.encode(encoding="utf-8"), digestmod=hashlib.sha256)
        return h.hexdigest().upper()

    def _post_request_data(self,api,parameters=None,payload=None, files=None,  headers=None):
        if headers is None:
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Odoo'
            }
        ir_config = self.env['ir.config_parameter'].sudo()
        data = payload or dict()
        timestamp = int(round(time.time() * 1000))

        sign = self.create_signature(api,parameters, timestamp)
        params = {"app_key": ir_config.get_param('intergrate_lazada.app_key', ''), "sign_method": "sha256",
                  "access_token": self.sudo().search([]).access_token, "timestamp": timestamp, "sign":sign}
        if parameters == dict():
            key = list(parameters.keys())[0]
            params.update({key: str(parameters[key])})
        else:
            params.update(parameters)

        url = ir_config.get_param('intergrate_lazada.url','') + api
        res = requests.post(
            url,
            data=data,
            params=params,
            files=files,
            headers=headers,
            verify=False
        )
        if res.status_code == 200:
            return res.json()

    def _get_request_data(self, api, parameters=None, payload=None, files=None, headers=None):
        if headers is None:
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Odoo'
            }
        if parameters is None:
            parameters = {}
        ir_config = self.env['ir.config_parameter'].sudo()
        data = payload or dict()
        timestamp = int(round(time.time() * 1000))

        sign = self.create_signature(api, parameters, timestamp)
        params = {"app_key": ir_config.get_param('intergrate_lazada.app_key', ''), "sign_method": "sha256",
                  "access_token": self.sudo().search([]).access_token, "timestamp": timestamp, "sign": sign}

        params.update(parameters)

        url = ir_config.get_param('intergrate_lazada.url', '') + api
        res = requests.get(
            url,
            data=data,
            params=params,
            files=files,
            headers=headers,
            verify=False
        )
        if res.status_code == 200:
            return res.json()

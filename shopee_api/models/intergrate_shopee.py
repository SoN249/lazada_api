from odoo import fields, models
import hmac
import json
import time
import hashlib
import requests

class IntergrateShopee(models.Model):
    _name="integrate.shopee"

    token = fields.Char(string="Token")

    def _create_signature(self,api, timest):
        ir_config = self.env['ir.config_parameter'].sudo()
        app_key = ir_config.get_param('shopee_api.app_key','')
        app_secret = ir_config.get_param('shopee_api.app_secret','')
        shop_id = ir_config.get_param('shopee_api.shop_id','')
        path = api
        tmp_base_string = "%s%s%s%s%s" % (app_key, path, timest, self.search([]).token, shop_id)
        base_string = tmp_base_string.encode()

        partner_key = app_secret.encode()
        sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()
        return sign

    def _get_data_shopee(self, api, payload=None, files=None, param=None, headers=None):
        if param is None:
            param = {}
        if headers is None:
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Odoo'
            }
        timest = int(time.time())
        sign = self._create_signature(api, timest)
        data = payload or dict()
        ir_config = self.env['ir.config_parameter'].sudo()
        params = {"partner_id": ir_config.get_param('shopee_api.app_key',''),
                  "access_token": self.search([]).token,
                  "sign": sign,
                  "timestamp": timest,
                  "shop_id": ir_config.get_param('shopee_api.shop_id','')
                  }
        params.update(param)
        url = ir_config.get_param('shopee_api.url','') + api
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


    def _post_data_shopee(self, api, payload=None, files=None, params={}, headers=None):
        if headers is None:
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Odoo'
            }
        data = payload or dict()
        url = "https://open-api-sandbox.tiktokglobalshop.com" + api
        res = requests.post(
            url,
            data=data,
            params=params,
            files=files,
            headers=headers,
            verify=False
        )
        print(res)
        if res.status_code == 200:
            return res.json()


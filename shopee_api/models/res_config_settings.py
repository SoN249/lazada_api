from odoo import fields, models
from odoo.exceptions import ValidationError
import hmac
import json
import time
import hashlib
import requests
class ResConfigSettingShopee(models.TransientModel):
    _inherit = "res.config.settings"

    app_key_shopee= fields.Integer("App key", config_parameter="shopee_api.app_key")
    app_secret_shopee = fields.Char("App secret",config_parameter="shopee_api.app_secret")
    auth_code_shopee = fields.Char("Auth code", config_parameter="shopee_api.auth_code")
    url_shopee = fields.Char("URL", config_parameter="shopee_api.url")
    shop_id = fields.Integer("Shop ID", config_parameter="shopee_api.shop_id")
    def btn_get_auth_shopee(self):
        if self.app_key_shopee and self.app_secret_shopee:
            timest = int(time.time())
            host = self.url_shopee
            path = "/api/v2/shop/auth_partner"
            redirect_url = "https://shopee.vn/"
            partner_id = self.app_key_shopee
            tmp = self.app_secret_shopee
            partner_key = tmp.encode()
            tmp_base_string = "%s%s%s" % (partner_id, path, timest)
            base_string = tmp_base_string.encode()
            sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()
            ##generate api
            url = host + path + "?partner_id=%s&timestamp=%s&redirect=%s&sign=%s"%(
            partner_id, timest, redirect_url, sign)
            return {
                'name': 'Authorization',
                'type': 'ir.actions.act_url',
                'url': url,  # Replace this with tracking link
                'target': 'new',  # you can change target to current, self, new.. etc
            }
        else:
            raise ValidationError("Invalid Client ID")

    def get_token_account_level(self):
        timest = int(time.time())
        host = self.url_shopee
        path = "/api/v2/auth/token/get"
        body = {"code": self.auth_code_shopee, "shop_id": self.shop_id, "partner_id": self.app_key_shopee}
        tmp_base_string = "%s%s%s" % (self.app_key_shopee, path, timest)
        base_string = tmp_base_string.encode()
        partner_key = self.app_secret_shopee.encode()
        sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()

        url = host + path + "?partner_id=%s&timestamp=%s&sign=%s" % (self.app_key_shopee, timest, sign)
        headers = {"Content-Type": "application/json"}
        resp = requests.post(url, json=body, headers=headers)
        res = json.loads(resp.content)
        access_token = res.get("access_token")
        new_refresh_token = res.get("refresh_token")
        print(res)
        if access_token:
            token = self.env['integrate.shopee'].sudo().search([])
            if not token:
                self.env['integrate.shopee'].sudo().create({"token": access_token})
            else:
                token.sudo().write({"token": access_token})









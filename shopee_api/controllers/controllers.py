# -*- coding: utf-8 -*-
# from odoo import http


# class ShopeeApi(http.Controller):
#     @http.route('/shopee_api/shopee_api', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/shopee_api/shopee_api/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('shopee_api.listing', {
#             'root': '/shopee_api/shopee_api',
#             'objects': http.request.env['shopee_api.shopee_api'].search([]),
#         })

#     @http.route('/shopee_api/shopee_api/objects/<model("shopee_api.shopee_api"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('shopee_api.object', {
#             'object': obj
#         })

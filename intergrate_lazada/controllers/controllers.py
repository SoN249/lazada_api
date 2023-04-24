# -*- coding: utf-8 -*-
# from odoo import http


# class IntergrateLazada(http.Controller):
#     @http.route('/intergrate_lazada/intergrate_lazada', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/intergrate_lazada/intergrate_lazada/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('intergrate_lazada.listing', {
#             'root': '/intergrate_lazada/intergrate_lazada',
#             'objects': http.request.env['intergrate_lazada.intergrate_lazada'].search([]),
#         })

#     @http.route('/intergrate_lazada/intergrate_lazada/objects/<model("intergrate_lazada.intergrate_lazada"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('intergrate_lazada.object', {
#             'object': obj
#         })

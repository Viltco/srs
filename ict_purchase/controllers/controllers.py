# -*- coding: utf-8 -*-
# from odoo import http


# class IctPurchase(http.Controller):
#     @http.route('/ict_purchase/ict_purchase/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ict_purchase/ict_purchase/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ict_purchase.listing', {
#             'root': '/ict_purchase/ict_purchase',
#             'objects': http.request.env['ict_purchase.ict_purchase'].search([]),
#         })

#     @http.route('/ict_purchase/ict_purchase/objects/<model("ict_purchase.ict_purchase"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ict_purchase.object', {
#             'object': obj
#         })

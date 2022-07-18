# -*- coding: utf-8 -*-
# from odoo import http


# class PropertyInvoiceBill(http.Controller):
#     @http.route('/property_invoice_bill/property_invoice_bill/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/property_invoice_bill/property_invoice_bill/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('property_invoice_bill.listing', {
#             'root': '/property_invoice_bill/property_invoice_bill',
#             'objects': http.request.env['property_invoice_bill.property_invoice_bill'].search([]),
#         })

#     @http.route('/property_invoice_bill/property_invoice_bill/objects/<model("property_invoice_bill.property_invoice_bill"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('property_invoice_bill.object', {
#             'object': obj
#         })

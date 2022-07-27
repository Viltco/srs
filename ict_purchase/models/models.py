# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class ict_purchase(models.Model):
#     _name = 'ict_purchase.ict_purchase'
#     _description = 'ict_purchase.ict_purchase'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

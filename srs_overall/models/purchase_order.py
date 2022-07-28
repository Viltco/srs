# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PurchaseInh(models.Model):
    _inherit = 'purchase.order'

    order_type = fields.Char(string="Purchase Order Type")
    building_unit = fields.Many2one('product.product', string="Building / Unit", domain=lambda self: [("property_book_for", "=", 'rent')])
    contract_no = fields.Char(string="Contract No.")


class PurchaseLineInh(models.Model):
    _inherit = 'purchase.order.line'

    net_amount = fields.Float(string="Net Amount", compute='_compute_net_amount')
    tax_amount = fields.Float(string='Tax Amount', compute='_compute_tax_amount')

    @api.depends('taxes_id')
    def _compute_tax_amount(self):
        for record in self:
            if record.taxes_id:
                for recs in record.taxes_id:
                    if recs:
                        record.tax_amount = (record.price_unit * recs.amount) / 100
                    else:
                        record.tax_amount = 0
            else:
                record.tax_amount = 0

    @api.depends('tax_amount')
    def _compute_net_amount(self):
        for record in self:
            record.net_amount = record.price_subtotal + record.tax_amount

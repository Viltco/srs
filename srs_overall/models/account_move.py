# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountMoveInh(models.Model):
    _inherit = 'account.move'

    building_unit = fields.Many2one('product.product', string="Building / Unit", domain=lambda self: [("property_book_for", "=", 'rent')])
    contract_no = fields.Char(string="Contract No.")


class AccountMoveLineInh(models.Model):
    _inherit = 'account.move.line'

    net_amount = fields.Float(string="Net Amount", compute='_compute_net_amount')
    tax_amount = fields.Float(string='Tax Amount', compute='_compute_tax_amount')

    @api.depends('tax_ids', 'price_unit')
    def _compute_tax_amount(self):
        for record in self:
            if record.tax_ids:
                for recs in record.tax_ids:
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

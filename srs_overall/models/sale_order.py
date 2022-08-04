# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleInh(models.Model):
    _inherit = 'sale.order'

    building_unit = fields.Many2one('product.product', string="Building / Unit", domain=lambda self: [("property_book_for", "=", 'rent')])
    contract_no = fields.Char(string="Contract No.")

    def performa_invoice_wizard(self):
        action = self.env.ref('srs_overall.action_performa_invoice_wizard').read()[0]
        return action


class SaleLineInh(models.Model):
    _inherit = 'sale.order.line'

    net_amount = fields.Float(string="Net Amount", compute='_compute_net_amount')
    tax_amount = fields.Float(string='Tax Amount', compute='_compute_tax_amount')

    @api.depends('tax_id')
    def _compute_tax_amount(self):
        for record in self:
            if record.tax_id:
                for recs in record.tax_id:
                    if recs:
                        record.tax_amount = (record.price_subtotal * recs.amount) / 100
                    else:
                        record.tax_amount = 0
            else:
                record.tax_amount = 0

    @api.depends('tax_amount')
    def _compute_net_amount(self):
        for record in self:
            record.net_amount = record.price_subtotal + record.tax_amount


class SaleAdvancePaymentInh(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    invoice_type = fields.Selection([('commercial', 'Commercial Rental Invoice'),
                                     ('cross', 'Cross Charge Invoice'),
                                     ('management', 'Management Fee - Invoice'),
                                     ('residential', 'Residential Rental Invoice'),
                                     ('non_tax', 'Non Tax Invoice'),
                                     ('other_income', 'Other Income Invoice')
                                     ], string='Type of Invoice')



# -*- coding: utf-8 -*-

from odoo.exceptions import UserError, ValidationError, Warning
from datetime import datetime
from datetime import date
from odoo import api, fields, models, _


class OfferLetter(models.Model):
    _name = 'offer.letter'
    _description = 'Offer Letter'
    _rec_name = 'multi_unit'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    multi_unit = fields.Char(string='Multi Units', tracking=True)
    multi_service = fields.Char(string='Multi Services', tracking=True)
    rent = fields.Char(string='Rent', tracking=True)
    period = fields.Char(string='Period', tracking=True)
    security_deposit = fields.Char(string='Security Deposit', tracking=True)
    validity_period = fields.Char(string='Validity Period', tracking=True)
    amount_tax = fields.Float(string='Tax Amount', tracking=True)
    description = fields.Char(string='Description', tracking=True)
    date = fields.Date(string='Date', tracking=True, default=fields.date.today())
    letter_type = fields.Selection([('residential', 'Residential'),
                              ('commercial', 'Commercial')
                              ], string='Offer Letter Type', tracking=True, index=True, copy=False)
    state = fields.Selection([('draft', 'Draft'),
                              ('review', 'Review'),
                              ('approve', 'Approve'),
                              ('confirmed', 'Confirmed'),
                              ('rejected', 'Rejected')
                              ], string='State', tracking=True, default='draft', readonly=True, index=True, copy=False)

    def button_send_review(self):
        self.write({
            'state': 'review'
        })

    def button_review(self):
        self.write({
            'state': 'approve'
        })

    def button_approve(self):
        self.write({
            'state': 'confirmed'
        })

    def button_rejected(self):
        self.write({
            'state': 'rejected'
        })

    def unlink(self):
        for record in self:
            if record.state == 'confirmed':
                raise UserError(_('Record cannot be deleted on confirmed state'))

# -*- coding: utf-8 -*-

import datetime
from lxml import etree
from odoo import models, fields, api, _
from datetime import timedelta
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from odoo.tools import float_compare


class PDCPayment(models.Model):
    _name = 'pdc.payment'
    _description = 'PDC Payment'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', tracking=True)
    partner_id = fields.Many2one('res.partner', string='Partner', tracking=True)
    bank_id = fields.Many2one('res.partner.bank', string='Bank', tracking=True)
    payment_amount = fields.Float(string='Payment Amount', tracking=True)
    cheque_ref = fields.Char(string='Commercial Name', tracking=True)
    memo = fields.Char(string='Memo', tracking=True)
    destination_account_id = fields.Many2one('account.account', string='Destination Account', tracking=True)
    journal_id = fields.Many2one('account.journal', string='Journal', tracking=True)
    currency_id = fields.Many2one('res.currency', string='Currency', tracking=True)
    pdc_type = fields.Selection([('sent', 'Sent'),
                              ('received', 'Received'),
                              ], string='PDC Type', tracking=True)

    # Date Fields

    date_payment = fields.Date(string='Payment Date', tracking=True)
    date_due = fields.Date(string='Due Date', tracking=True)
    date_cleared = fields.Date(string='Cleared Date', tracking=True)
    date_return = fields.Date(string='Return Date', tracking=True)
    date_deposit = fields.Date(string='Deposit Date', tracking=True)
    date_bounced = fields.Date(string='Bounced Date', tracking=True)

    # State Field

    state = fields.Selection([('draft', 'Draft'),
                              ('save', 'Save'),
                              ('registered', 'Registered'),
                              ('returned', 'Returned'),
                              ('deposited', 'Deposited'),
                              ('bounced', 'Bounced'),
                              ('cleared', 'Cleared'),
                              ('cancel', 'Cancel'),
                              ], string='State', default='draft', tracking=True, readonly=True, index=True, copy=False)

    def check_balance(self):
        partner_ledger = self.env['account.move.line'].search(
            [('partner_id', '=', self.partner_id.id),
             ('move_id.state', '=', 'posted'), ('full_reconcile_id', '=', False), ('balance', '!=', 0),
             ('account_id.reconcile', '=', True), ('full_reconcile_id', '=', False), '|',
             ('account_id.internal_type', '=', 'payable'), ('account_id.internal_type', '=', 'receivable')])
        bal = 0
        for par_rec in partner_ledger:
            bal = bal + (par_rec.debit - par_rec.credit)

    def action_pdc_payment_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Partner Ledger Report',
            'view_id': self.env.ref('pdc_payments.view_pdc_payment_wizard_form', False).id,
            # 'context': {'default_ref': self.name, 'default_order_amount': self.amount_total, 'default_user_id': self.user_id.id},
            'target': 'new',
            'res_model': 'pdc.payment.wizard',
            'view_mode': 'form',
        }

    @api.model
    def create(self, vals):
        sequence = self.env.ref('pdc_payments.pdc_payment_seq')
        vals['name'] = sequence.next_by_id()
        rec = super(PDCPayment, self).create(vals)
        return rec

    def button_save(self):
        self.write({
            'state': 'save'
        })

    def button_register(self):
        self.write({
            'state': 'registered'
        })

    def button_cancel(self):
        self.write({
            'state': 'cancel'
        })

    def button_return(self):
        self.write({
            'state': 'returned'
        })

    def button_deposit(self):
        self.write({
            'state': 'deposited'
        })

    def button_bounce(self):
        self.write({
            'state': 'bounced'
        })

    def button_cleared(self):
        self.write({
            'state': 'cleared'
        })
        vals = {
            'journal_id': self.journal_id.id,
            'user_id': self.env.user.id,
            'payment_type': 'inbound' if self.pdc_type == 'received' else 'outbound',
            'partner_type': 'customer' if self.pdc_type == 'received' else 'supplier',
            'partner_id': self.partner_id.id,
            'partner_bank_id': self.bank_id.id,
            'destination_account_id': self.destination_account_id.id,
            'date': self.date_cleared,
            'amount': self.payment_amount,
            'ref': self.memo,
            'pdc_ref': self.name,
            'currency_id': self.currency_id.id,
        }
        payment = self.env['account.payment'].create(vals)
        print(payment.partner_type)
        # else:
        #     vals = {
        #         'journal_id': self.journal_id.id,
        #         'user_id': self.env.user.id,
        #         'payment_type': 'outbound',
        #         'partner_type': 'supplier',
        #         'partner_id': self.partner_id.id,
        #         'partner_bank_id': self.bank_id.id,
        #         'destination_account_id': self.destination_account_id.id,
        #         'date': self.date_cleared,
        #         'amount': self.payment_amount,
        #         'ref': self.memo,
        #         'pdc_ref': self.name,
        #         'currency_id': self.currency_id.id,
        #     }
        #     payment = self.env['account.payment'].create(vals)


class AccountPaymentInherit(models.Model):
    _inherit = 'account.payment'

    pdc_ref = fields.Char(string='PDC Reference', tracking=True)
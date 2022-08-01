# -*- coding: utf-8 -*-

from random import choice
from string import digits
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PartnerInh(models.Model):
    _inherit = "res.partner"

    iban_no = fields.Char(string='IBAN')
    customer_id = fields.Char(string='Customer ID')
    branch = fields.Char(string='Branch')

    barcode = fields.Char(string='Code')

    _sql_constraints = [
        ('barcode_uniq', 'unique (barcode)',
         "The Code must be unique, this one is already assigned to another employee."),
        # ('user_uniq', 'unique (user_id, company_id)',
        #  "A user cannot be linked to multiple employees in the same company.")
    ]

    def generate_random_barcode(self):
        for partner in self:
            partner.barcode = '042' + "".join(choice(digits) for i in range(9))


class PartnerBankInh(models.Model):
    _inherit = "res.partner.bank"

    remarks = fields.Char(string='Remarks')

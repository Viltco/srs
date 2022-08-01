from odoo import api, fields, models, _
from datetime import date


class TenancyContract(models.Model):
    _name = "tenancy.contract"
    _description = "Tenancy Contract"
    _rec_name = 'property_usage'

    property_usage = fields.Selection([
        ('industrial', 'Industrial'),
        ('commercial', 'Commercial'),
        ('residential', 'Residential'),
    ])
    date = fields.Date(string='Date')
    number = fields.Char(string='Number')
    landlord_name = fields.Many2one('res.partner', string='Landlord Name')
    tenant_name = fields.Many2one('res.partner', string='Tenant Name')
    tenant_email = fields.Char(string='Tenant Email')
    landlord_email = fields.Char(string='Landlord Email')
    tenant_phone = fields.Char(string='Tenant Phone')
    landlord_phone = fields.Char(string='Landlord Phone')
    building_name = fields.Char(string='Building Name')
    location = fields.Char(string='Location')
    property_size = fields.Integer(string='Property Size(S.M)')
    property_type = fields.Char(string='Property Type')
    property_no = fields.Integer(string='Property No')
    premises_no = fields.Integer(string='Premises No')
    plot_no = fields.Integer(string='Plot No')
    contact_period_to = fields.Date(string='To')
    contact_period_from = fields.Date(string='From')
    annual_rent = fields.Integer(string='Annual Rent')
    no_of_payment = fields.Integer(string='No of Payment')
    contract_value = fields.Integer(string='Contract Value')
    security_amount = fields.Integer(string='Security Deposit Amount')
    mode_of_payment = fields.Char(string='Mode of Payment')
    rental_rows = fields.Float(compute='_compute_rental_rows', invisible=True)

    state = fields.Selection(
        [('new', 'New'), ('review', 'Review'), ('approved', 'Approved'),
         ('cancel', 'Cancelled')],
        default='new')

    @api.depends('no_of_payment')
    def _compute_rental_rows(self):
        for record in self:
            if record.no_of_payment > 0:
                record.rental_rows = record.annual_rent / record.no_of_payment
            else:
                record.rental_rows = 0

    def action_review(self):
        self.state = 'review'

    def action_approve(self):
        self.state = 'approved'

    def action_cancel(self):
        self.state = 'cancel'


class ResPartnerField(models.Model):
    _inherit = 'res.partner'

    is_tenant = fields.Boolean(string='Is Tenant')
    is_landlord = fields.Boolean(string='Is Landlord')

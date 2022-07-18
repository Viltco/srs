from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class PDCPaymentWizard(models.TransientModel):
    _name = 'pdc.payment.wizard'
    _description = 'PDC Payment'

    date_start = fields.Date(string='Start Date')
    date_end = fields.Date(string='End Date')

    @api.constrains('date_start', 'date_end')
    def date_constrains(self):
        for rec in self:
            if rec.date_end < rec.date_start:
                raise ValidationError(_('End Date Must be Greater Than Start Date...'))

    #     model = self.env.context.get('active_model')
    #     rec = self.env[model].browse(self.env.context.get('active_id'))

    def apply_data(self):
        data = {
            'model': 'pdc.payment.wizard',
            'ids': self.ids,
            'form': {
                'date_start': self.date_start, 'date_end': self.date_end,
            },
        }
        return self.env.ref('pdc_payments.pdc_payment_report_id').report_action(self, data=data)

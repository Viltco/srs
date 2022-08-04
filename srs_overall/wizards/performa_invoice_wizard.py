import datetime

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError


class PerformaInvoiceWizard(models.TransientModel):
    _name = 'performa.invoice.wizard'

    name = fields.Selection([
        ('res_inv', 'Residential invoice'),
        ('com_inv', 'Commercial invoice')], string='Create Performa invoice')

    def open_proforma(self):
        record = self.env['sale.order'].browse(self.env.context.get('active_ids'))
        # for rec in record:
        record.action_quotation_send()
        self.create_invoices()

    def create_invoices(self):
        record = self.env['sale.order'].browse(self.env.context.get('active_ids'))
        print('move_type: out_invoice')
        line_vals = []
        for line in record.order_line:
            line_vals.append((0, 0, {
                'product_id': line.product_id.id,
                'name': line.name,
                'quantity': line.product_uom_qty,
                'price_unit':line.price_unit,
                'tax_ids':line.tax_id,
                'tax_amount': line.tax_amount,
                'net_amount': line.net_amount,
                'price_subtotal': line.price_subtotal
            }))
        print(line_vals)
        inv = {
            'invoice_origin': record.name,
            'invoice_line_ids': line_vals,
            'partner_id': record.partner_id.id,
            'move_type': 'out_invoice',
            'invoice_date':datetime.date.today(),
            'invoice_payment_term_id':record.payment_term_id
        }
        invoice = self.env['account.move'].create(inv)

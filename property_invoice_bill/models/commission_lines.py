from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date,datetime
from dateutil.relativedelta import relativedelta

# 
class AccountCommission(models.Model):
    _inherit="account.move"
     
    commission_id=fields.Many2one('commission.line' ,string='Commission ID')
    
    
    def action_post(self):
        res= super(AccountCommission , self).action_post()
        if self.move_type == 'in_invoice' and self.commission_id != False:
            self.commission_posted()
        return res
    
    
    
    def commission_posted(self):
       
        obj = self.commission_id
        if obj:
            obj.state = 'posted'
    
    
    
    def commission_paid(self):
       
        obj = self.commission_id
        if obj:
            obj.state = 'paid'
     
    def general_entry(self):
        line_ids = []
        debit_sum = 0.0
        credit_sum = 0.0
        misc_journal = self.env['account.journal'].search([('type','in',['general'])],limit=1)
        debit_account = self.env['account.account'].search([('name','=','Commission expense')],limit=1)
        credit_account = self.env['account.account'].search([('name','=','Commission payable')],limit=1)
        move_dict = {
            'name': self.name,
            'journal_id': misc_journal.id,
            'partner_id': self.commission_id.property_id.owner_id.id,
            'date': self.invoice_date_due,
            'state': 'draft',
        }
#         for oline in self.move_lines:
        debit_line = (0, 0, {
            'name': self.commission_id.name,
            'debit': abs(self.commission_id.commission),
            'credit': 0.0,
            'partner_id':self.commission_id.property_id.owner_id.id,
            # 'analytic_account_id': oline.analytic_account_id.id,
            # 'analytic_tag_ids': [(6, 0, oline.analytic_tag_ids.ids)],
            'account_id':debit_account.id,
        })
        line_ids.append(debit_line)
#         debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']
        credit_line = (0, 0, {
            'name': self.commission_id.name,
            'debit': 0.0,
            'partner_id':self.commission_id.property_id.owner_id.id,
            'credit': abs(self.commission_id.commission),
            'account_id': credit_account.id,
        })
        line_ids.append(credit_line)
#         credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']

        move_dict['line_ids'] = line_ids
        move = self.env['account.move'].create(move_dict)
        print("General entry created")


class CommissionAccountPaymentRegisterinh(models.TransientModel):
    _inherit= 'account.payment.register'
    
    
    
  
    
    def _create_payments(self):
        res= super(CommissionAccountPaymentRegisterinh , self)._create_payments()
        if self.env.context.get('active_id' ,False):
             
            move_id = self.env['account.move'].search([('id','=',self.env.context.get('active_id' ))])
            if move_id.move_type == 'in_invoice' and move_id.commission_id != False:
                move_id.commission_paid()
        return res
    
    
    
    
    
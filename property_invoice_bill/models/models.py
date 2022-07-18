# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date,datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import Warning,ValidationError,UserError


class property_invoice_bill(models.TransientModel):
    _inherit = 'property.book'
    _description = 'property_invoice_bill.property_invoice_bill'
    
    payment_terms= fields.Selection([('annualy','Annualy'),('bi_annualy','Biannualy'),
                                     ('quarterly','Quarterly'),('monthly','Monthly'),
                                     ('weekly','Weekly')
                                     ],string="Payment terms")
    
    
    
    
    
    def get_diff_months(self , date_to, date_from):
        return (date_to.year - date_from.year) * 12 + date_to.month - date_from.month
    
    
    def getTotalInvoiceBill(self , payment_term , contract_months):
        info =[]
        if payment_term == 'annualy':
#             no_of_invoice_bill = int(12/12)  
            if contract_months < 12:
                no_of_invoice_bill = divmod(contract_months ,contract_months)
                info.append(no_of_invoice_bill)
                info.append(contract_months)  
            else:    
                no_of_invoice_bill = divmod(contract_months ,12)
                info.append(no_of_invoice_bill)
                info.append(12)  
        elif payment_term == 'bi_annualy':
#             no_of_invoice_bill = int(12/6)
            if contract_months < 6:
                no_of_invoice_bill = divmod(contract_months ,contract_months)
                info.append(no_of_invoice_bill)
                info.append(contract_months)  
            else:    
                no_of_invoice_bill =  divmod(contract_months ,6)
                info.append(no_of_invoice_bill)
                info.append(6)        
                
        elif  payment_term == 'quarterly':
#             no_of_invoice_bill = int(12/3)
            if contract_months < 3:
                no_of_invoice_bill = divmod(contract_months ,contract_months)
                info.append(no_of_invoice_bill)
                info.append(contract_months)
            else:       
                no_of_invoice_bill = divmod(contract_months , 3)
                info.append(no_of_invoice_bill)
                info.append(3)
              
        elif  payment_term == 'monthly':
#             no_of_invoice_bill = contract_months   
            no_of_invoice_bill = divmod(contract_months , 1)
            info.append(no_of_invoice_bill)
            info.append(1) 
        elif  payment_term == 'weekly':
            diff =self.to_date - self.from_date
            no_of_invoice_bill =   divmod(diff.days , 7)
            info.append(no_of_invoice_bill) 
            info.append(7)
        return info 
    

                 
    def calculateCommission(self, value):
        if self.property_id.commission_type == 'percentage':
            agent_commission= (self.property_id.commission_amount  * value) /100
            return agent_commission
         
        if self.property_id.commission_type == 'fixed':
            agent_commission = self.property_id.commission_amount #*  (conract_months/no_of_invoice_bill)
            return agent_commission
                        
    
    
    def CreateInvoiceBill(self,amount,account_id,invoice=False ,bill=False ):
        account_inv_obj = self.env['account.move']
        if invoice == True:
            acc_type = 'out_invoice'
            partner_id = self.property_id.tenant_id
        if bill == True:
            acc_type = 'in_invoice'
            partner_id = self.property_id.owner_id    
            
        vals  = {
            'property_id':self.property_id.id,
            'move_type': acc_type,
            'invoice_origin':self.property_id.name,
            'partner_id': partner_id.id,
            'invoice_user_id':self.renter_id.id or self.property_id.salesperson_id.id,
            'invoice_line_ids': [(0,0,{
                'name':self.property_id.name,
                'product_id':self.property_id.id,
                'account_id': account_id,
                'price_unit': amount })],
            }
            
        invoice_id = account_inv_obj.create(vals)
        
        return invoice_id
    
    
    
    
    
    def generateContractBasedBillIvoice(self):
        try:
            
            if self.property_id.property_account_income_id:
                income_account = self.property_id.property_account_income_id.id
            elif self.property_id.categ_id.property_account_income_categ_id:
                income_account = self.property_id.categ_id.property_account_income_categ_id.id  
            
            contract_months = self.contract_id.month
               
            no_of_invoice_bill = self.getTotalInvoiceBill(self.payment_terms ,contract_months)
#             invoice_amount = self.rent_price * (contract_months/no_of_invoice_bill)
#             
#             commission_amount = self.calculateBillAmount(invoice_amount, no_of_invoice_bill,contract_months)
#             bill_amount = invoice_amount - commission_amount
            invoices_list =[]
            bills_list = []
            invoice_bill_date = self.from_date.replace(day=1)
            count=0
            if no_of_invoice_bill[0][1] == 0:
                num =  sum(no_of_invoice_bill[0])
            elif  no_of_invoice_bill[0][1] != 0:
                num= sum((no_of_invoice_bill[0][0],1))   
#             for i in range(0,sum(no_of_invoice_bill[0])):
#             for i in range(0,sum((no_of_invoice_bill[0][0],1))): #combined remaining months amount
            for i in range(0,num):
                ''' 
                   create invoice according to payment terms
                '''
                count = count +1 
                months_period =0
                if count <= no_of_invoice_bill[0][0]:
                    invoice_amount = self.rent_price * no_of_invoice_bill[1]
                    commission_amount = self.calculateCommission(invoice_amount)
                    if self.property_id.commission_type == 'fixed':
                        commission_amount =commission_amount * no_of_invoice_bill[1]
                    bill_amount = invoice_amount - commission_amount
                    months_period = no_of_invoice_bill[1]
                else:
#                     invoice_amount = self.rent_price                
                    invoice_amount = self.rent_price * no_of_invoice_bill[0][1]  #combined remaining months amount
                    commission_amount = self.calculateCommission(invoice_amount)
                    bill_amount = invoice_amount - commission_amount
                    months_period = 1
                     
                    
                invoice_id = self.CreateInvoiceBill(invoice_amount, income_account,invoice = True)
                invoice_id.invoice_date = invoice_bill_date
                invoices_list.append(invoice_id)
                
                
                
                ''' 
                   create commissioned bills according to payment terms
                '''
                bill_id   =  self.CreateInvoiceBill(bill_amount, income_account,bill = True)    
                bill_id.invoice_date = invoice_bill_date
                bills_list.append(bill_id)
                
                commission_id = self.env['commission.line'].create({'name': self.property_id.owner_id.name,
                                                                    'property_id': self.property_id.id,
                                                                    'inv_pay_source':bill_id.name,
                                                                    'user_id':self.property_id.salesperson_id.id,
                                                                    'percentage':self.property_id.commission_amount,
                                                                    'commission' : commission_amount,
                                                                    'invoice_id':bill_id.id,
                                                                    'invoice_date':bill_id.invoice_date})
                
                bill_id.commission_id = commission_id.id
                invoice_bill_date  =invoice_bill_date + relativedelta(months =months_period)   
#                 if self.payment_terms != 'weekly':
#                     invoice_bill_date = invoice_bill_date + relativedelta(months = (contract_months/no_of_invoice_bill)) 
#                 else:
#                     invoice_bill_date = invoice_bill_date + relativedelta(days = 7)  
                 
            return [{'message':'sucessfully created!!'}]    
        except Exception as e:
             raise ValidationError(_(e.args))           
        
    
    
    
    def create_rent_contract(self):
        res= super(property_invoice_bill , self).create_rent_contract()
        if self.property_id.property_book_for == 'rent':
            bill_invoices = self.generateContractBasedBillIvoice()
         
        return res

class ContractProductProduct(models.Model):
    _inherit = 'product.product'
    
    tenant_id = fields.Many2one('res.partner', string='Tenant')
    commission_type = fields.Selection([('fixed','Fixed'),('percentage','Percentage')],string="Commission Type")
    commission_amount =fields.Float(string ='Commission amount')
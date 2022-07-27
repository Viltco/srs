# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from lxml import etree
from random import randint


class IctSalePurchaseInherit(models.Model):
    _inherit="sale.order"
     
    po_count = fields.Integer(compute='compute_po_count')
    def compute_po_count(self):
        for rec in self:
            order_count = self.env['purchase.order'].search_count([('ref_sale_id.id', '=', rec.id)])
            rec.po_count = order_count
#     '''change request'''
#     def action_confirm(self):
#         res = super(IctSalePurchaseInherit,self).action_confirm()
#         return self.action_open_create_po_wizard(res)
        
  
    
    def action_open_create_po_wizard(self):
        
        so_lines = []
        if self.order_line:
            
            for so_line in self.order_line: #loop for multiple lines.
                taxes_id = so_line.tax_id
                so_lines.append((0,0, {
                    'product_id' : so_line.product_id.id,
                    'product_uom_qty' : so_line.product_uom_qty, 
    #                 'description' : pr_line.name,
                    'price_unit' : so_line.price_cost,
                    'tax_id': [(6, 0, taxes_id.ids)],
                    'product_uom' : so_line.product_uom.id,
                }))
        
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Purchase Order',
            'view_id': self.env.ref('ict_purchase.view_create_purchase_wizard_form', False).id,
            'target': 'new',
            'context':{'default_wizard_line': so_lines},
            'res_model': 'purchase.sale.wizard',
            'view_mode': 'form',
        }
    
    
    
    def smart_purchase_button(self):
        return {
            'name': _('Purchase order'),
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'domain': [('ref_sale_id', '=', self.id)],
            'type': 'ir.actions.act_window',
        }

    
    
class IctPurchase(models.Model):
    _inherit  = 'purchase.order'

    picking_state = fields.Selection([
        ('pending', 'Pending'),
        ('partial', 'Partial'),
        ('full', 'Received'),
        ('no_receipt', ' '),
    ], string='Receipt Status', copy=False, index=True, tracking=True, compute='_compute_picking_state')

    @api.depends('order_line')
    def _compute_picking_state(self):

        for record in self:
            dmd = 0
            rcvd = 0
            if record.order_line:
                for rec in record.order_line:
                    dmd = dmd + rec.product_qty
                    rcvd = rcvd + rec.qty_received
                if rcvd == 0:
                    record.picking_state = 'pending'
                elif dmd - rcvd != 0:
                    record.picking_state = 'partial'
                elif dmd - rcvd == 0:
                    record.picking_state = 'full'
            else:
                record.picking_state = 'no_receipt'

    def _get_default_color(self):
        return randint(1, 11)


    color = fields.Integer(string='Color Index', default=_get_default_color)
    
    ref_sale_id =fields.Many2one('sale.order',string ='Sale Order Ref', readonly=True)
    sale_partner_id =fields.Many2one('res.partner',string ='Customer', related='ref_sale_id.partner_id')

    receipt_status = fields.Selection([
        ('no_receipt', ' '),
        ('merge','  '),
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('assigned', 'Ready'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Receipt Status', compute='_compute_receipt_state',
        copy=False, index=True, readonly=True, tracking=True,
     )

#     @api.depends('picking_ids')
    def _compute_receipt_state(self):
        for rec in self:
            if rec.picking_ids:
                picking_sorted = rec.picking_ids.sorted(key ='id')
                rec.receipt_status = picking_sorted[-1].state
            else:
                rec.receipt_status= 'no_receipt'


# class PurchaseMail(models.TransientModel):
#     _inherit = 'mail.compose.message'
#
#     def action_send_mail(self):
#         res = super(PurchaseMail, self).action_send_mail()
#         template_id = self.env.ref('dicker_data_invoice.purchase_order_data_report').id
#         template = self.env['mail.template'].browse(template_id)
#         template.send_mail(self.id, force_send=True)
#         return res
                
            
    


    
    

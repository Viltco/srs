from odoo import api,fields,models,_



class AccountEdi(models.Model):
    _inherit = 'account.edi.document'

    def action_export_xml(self):
        pass


class WizardPurchaseFromSale(models.TransientModel):
    _name = 'purchase.sale.wizard'

    partner_id =  fields.Many2one('res.partner', string='Vendor')
    wizard_line = fields.One2many('purchase.sale.line.wizard', 'purchase_sale_wizard_id',  string='SO Lines',)

    
#     
#     def assign_po_to_product(self,recs):
#         for p in recs:
            
    
    
#     @api.onchange('partner_id')
#     def get_active_model_ids(self):
#         if self.env.context.get('active_id'):
#             return {'domain': {'partner_id': [('id', 'in',[230])]}}
    
    
    def action_create_purchase_order(self):
        model = self.env.context.get('active_model')
        rec_model = self.env[model].browse(self.env.context.get('active_id'))
        
#         partner = self.partner_id.id
        partner_ids = self.wizard_line.mapped('partner_id')
        partner_po_list = []
        prod_part =[]
        po_list =[]
        
        
        for partner in partner_ids:
            partner_po_list = []
         
            partner_po_lines = self.wizard_line.filtered(lambda r,partnr = partner:r.partner_id ==  partnr)
            for record in partner_po_lines:
                taxes_id = record.tax_id
       
                
                partner_po_list.append((0, 0, {
                            'product_id': record.product_id.id,
                            'name': record.product_id.name,
                            'product_qty': record.product_uom_qty,
                            'product_uom': record.product_uom.id,
                            'price_unit': record.price_unit,
                            'taxes_id': [(6, 0, taxes_id.ids)]

                        }
                    ))
            po_vals = {
                    'partner_id': partner.id,
                    'currency_id': self.env.user.company_id.currency_id.id,
                    'date_order': fields.Date.today(),
                    'company_id': rec_model.company_id.id,
                    'order_line': partner_po_list,
                    'ref_sale_id':rec_model.id

                }

            purchase_order = self.env['purchase.order'].create(po_vals)
            for prd in partner_po_lines:
                prd.product_id.po_ids = prd.product_id.po_ids + purchase_order
                prd.product_id.product_tmpl_id.po_ids =  prd.product_id.product_tmpl_id.po_ids + purchase_order
                
            print (purchase_order)
        
        
        

                            
class WizardPurchaseFromSaleLine(models.TransientModel):
    _name='purchase.sale.line.wizard'
    
    product_id= fields.Many2one('product.product', string= 'Product')
    product_uom_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True, default=1.0)
    product_uom = fields.Many2one('uom.uom')
    purchase_sale_wizard_id = fields.Many2one('purchase.sale.wizard',string="ps_wizard")
    tax_id = fields.Many2many('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])
    price_unit = fields.Float('Cost Price', required=True, digits='Product Price', default=0.0)
    partner_id =fields.Many2one('res.partner', string='Vendor', domain=lambda self: [("supplier_rank", ">=", 1)])

    dicker_data = fields.Float(string='Dicker Data', related = 'product_id.dicker_data')
    leader_data = fields.Float(string='Leader' , related = 'product_id.leader_data')
    ingram_micro_data = fields.Float(string='Ingram Micro', related = 'product_id.ingram_micro_data')
    synexx_data = fields.Float(string='Synnex', related = 'product_id.synexx_data')

    dicker_qty = fields.Char('DickerData Stock', related = 'product_id.dicker_qty')
    leader_qty = fields.Char('Leader Stock' , related = 'product_id.leader_qty')
    ingram_qty = fields.Char('Ingram Stock' ,related = 'product_id.ingram_qty')
    synnex_qty = fields.Char('Synnex Stock' ,related = 'product_id.synnex_qty')




   
   
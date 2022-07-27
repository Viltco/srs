from odoo import api,models, fields, _
from lxml import etree
from random import randint
from pickle import FALSE

class ICTPoProduct(models.Model):
    _inherit ="product.template"
    
     
  
    po_ids = fields.Many2many("purchase.order", 'product_purchase_rel','product_id', 'purchase_id',readonly= False, string="PO Refs", track_visibility='always')
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AssetsInh(models.Model):
    _inherit = 'account.asset'

    account_group_id = fields.Many2one('account.group', string="Group", copy=False)
    sub_group = fields.Char(string="Sub Group", copy=False)
    brand = fields.Char(string="Brand", copy=False)
    location_id = fields.Many2one('stock.location', string="Location", copy=False)
    custodian = fields.Char(string="Custodian", copy=False)

    asset_code = fields.Char(string="Asset Code", copy=False)

    @api.model
    def create(self, vals):
        group_record = self.env['account.group'].browse(vals['account_group_id'])
        group_code = group_record.name
        location_record = self.env['stock.location'].browse(vals['location_id'])
        location_code = location_record.name
        asset_code = (group_code + '-' + vals['sub_group'] + '-' + vals['brand'] + '-' + location_code + '-' + vals['custodian'])
        vals['asset_code'] = asset_code
        res = super(AssetsInh, self).create(vals)
        return res

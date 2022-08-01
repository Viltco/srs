from odoo import api, fields, models, _


class ResUsers(models.Model):
    _inherit = 'res.users'

    status = fields.Selection([
            ('active', 'Active'),
            ('inactive', 'InActive'),
        ] , string="Status")
    branch_id = fields.Many2one('model.branch' , string="Branch")
    display_on_branches = fields.Char(string='Display On Branches')

    designation = fields.Char(string='Designation' )
    phone = fields.Char(string='Telephone Number' )
    cell = fields.Char(string='Cell')
    id_passport = fields.Integer(string='ID Passpoprt')
    physical_address = fields.Text(string='Physical Address')
    postal_address = fields.Text(string='Postal Address')

    employment_date = fields.Date(string='Employment Date')
    resume = fields.Text(string='Resume')

    login_email = fields.Char(string='Login Email')
    user_group = fields.Many2one('res.groups' , string="User Group")

    facebook_url = fields.Char(string='Facebook URL')
    twitter_url = fields.Char(string='Twitter URL')
    linkedin_url = fields.Char(string='LInkedin URL')
    youtube_url = fields.Char(string='Youtube URL')
    blog_url = fields.Char(string='Blog URL')
    pintrest_url = fields.Char(string='Pintrest URL')
    instagram_url = fields.Char(string='Instagram URL')

    fidelity_fund_id = fields.Many2many(comodel_name="ir.attachment",
                                       relation="m2m_ir_fidelity_fund_rel",
                                       column1="m2m_id",
                                       column2="attachment_id",
                                       )
    media_id = fields.Many2many(comodel_name="ir.attachment",
                                   relation="m2m_ir_media_rel",
                                   column1="m2m_id",
                                   column2="attachment_id",
                                   )
    document_id = fields.Many2many(comodel_name="ir.attachment",
                                relation="m2m_ir_document_id_rel",
                                column1="m2m_id",
                                column2="attachment_id",
                                )


















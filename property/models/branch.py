from odoo import api, fields, models, _


class Branch(models.Model):
    _name = "model.branch"
    _description = "Branch"
    _rec_name = 'branch_name'

    status = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'InActive'),
    ], string="Status")
    display_on_website = fields.Boolean(string='Display On Website')

    branch_name = fields.Char(string='Branch Name')
    head_office = fields.Boolean(string='Head Office')

    email = fields.Char(string='Email' )
    phone = fields.Char(string='Telephone Number')
    fax_no = fields.Integer(string='Fax Number')
    physical_address = fields.Text(string='Physical Address')
    postal_address = fields.Text(string='Postal Address')
    province = fields.Many2one('res.country.state' , string="Province")

    profile = fields.Text(string='Profile')

    website = fields.Char(string='Website')
    facebook_url = fields.Char(string='Facebook URL')
    twitter_url = fields.Char(string='Twitter URL')
    linkedin_url = fields.Char(string='LInkedin URL')
    youtube_url = fields.Char(string='Youtube URL')
    blog_url = fields.Char(string='Blog URL')
    pintrest_url = fields.Char(string='Pintrest URL')
    instagram_url = fields.Char(string='Instagram URL')

    feed_listing_facebook = fields.Boolean(string='Feed Listings to Faceook')
    feed_new_news_facebook = fields.Boolean(string='Feed New News Articles to Facebook')

    branch_image_id = fields.Many2many(comodel_name="ir.attachment",
                                relation="m2m_ir_branch_image_rel",
                                column1="m2m_id",
                                column2="attachment_id",
                                )
    document_id = fields.Many2many(comodel_name="ir.attachment",
                                relation="m2m_ir_document_rel",
                                column1="m2m_id",
                                column2="attachment_id",
                                )











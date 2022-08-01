from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResidentialProperty(models.Model):
    _name = "residential.property"
    _description = "Residential Property"
    _rec_name = 'web_reference'

    web_reference = fields.Integer(string='Web Reference')
    # tags = fields.Char(string='Tags')
    status = fields.Selection([
        ('active', 'Active'),
        ('archive', 'Archived'),
        ('sold', 'Sold'),
        ('rent', 'Rented'),
        ('transaction_pending', 'Transaction Pending'),
        ('valuation', 'Valuation'),
    ])
    branch_id = fields.Many2one('model.branch', string="Branch")
    team_id = fields.Many2one('crm.team', string="Team")
    agent = fields.Many2one('res.partner', string="Agent")
    agent_2 = fields.Many2one('res.partner', string="Agent 2")
    agent_3 = fields.Many2one('res.partner', string="Agent 3")
    agent_4 = fields.Many2one('res.partner', string="Agent 4")
    user_id = fields.Many2one('res.users', string="User" , default=lambda self:self.env.user.id)


    property_type_id = fields.Many2one('property.type', string="Property Type")
    location = fields.Many2one('area.details',string='Location')
    unit_number = fields.Integer(string='Unit Number')
    complex_name = fields.Integer(string='Complex Number')
    building_name = fields.Integer(string='Building Number')
    street_number = fields.Integer(string='Street Number')
    street_name = fields.Char(string='Street Name')
    publish_street_address = fields.Boolean(string='Publish Street Address')

    listing_type = fields.Selection([
        ('for_sale', 'For Sale'),
        ('for_rent', 'For Rent'),
    ], default='for_sale')
    plan_type = fields.Selection([
        ('ready', 'Ready'),
        ('off_plan', 'Off Plan'),
    ], default='ready')
    for_sale_price_on_app = fields.Boolean(string='Price On Application')
    for_sale_price = fields.Integer(string='Price')
    for_sale_valuation_price = fields.Integer(string='Valuation Price')
    # for_sale_distressed_sale = fields.Boolean(string='Distressed Sale')
    # for_sale_bank_repossesed = fields.Boolean(string='Bank Repossesed')

    for_rent_price_on_app = fields.Boolean(string='Price On Application', )
    for_rent_price = fields.Integer(string='Price')
    for_rent_price_term = fields.Selection([
        ('per_year', 'Per Year'),
    ], default='per_year', string="Price Term")
    for_rent_rental_valuation = fields.Boolean(string='Rental Valuation')

    land_size_measurement_type = fields.Selection([
        ('square_feet', 'Square Feet'),
        ('acres', 'Acres'),
    ], string="Plot Size")
    floor_size_measurement_type = fields.Selection([
        ('square_feet', 'Square Feet'),
        ('acres', 'Acres'),
    ], string=" B.U.A")
    developer = fields.Integer(string='Developer')
    # build_year = fields.Integer(string='Build Year')
    build_year = fields.Selection(
        selection='year_selection',
        string="Year",
        default="2022",  # as a default value it would be 2019
    )
    build_completion_status = fields.Selection([
        ('completed', 'Completed'),
        ('off_plan', 'OffPlan'),
    ])
    # linked_project = fields.Char(string='Linked Project')
    marketing_heading = fields.Char(string='Marketing Heading')
    description = fields.Text(string='Description')

    # @api.constrains('description')
    # def _check_len_html(self):
    #     if len(self.description) < 750 or len(self.description) > 2000:
    #         raise ValidationError("Character count (750-2000 words) Your number of words do not meet with the required count please enter required number of words")

    feature_amenities_id = fields.Many2one('feature.amenities', string="Feature Amenities")

    security = fields.Boolean(string='Security')
    pet_allowed = fields.Boolean(string='Pet Allowed')

    # mandate_details_id = fields.Many2one('mandate.details', string="Property Permit")

    # seller_id = fields.Many2one('res.partner', string="Seller")
    tenant_id = fields.Many2one('res.partner', string="Tenant")

    # viewing_contact_person = fields.Char(string='Viewing Contact Person')
    # viewing_contact_number = fields.Integer(string='Viewing Contact Number')
    # viewing_keys_available_form = fields.Integer(string='Viewing Keys Available From')
    # viewing_notes = fields.Char(string='Viewing Notes')

    external_link_name = fields.Char(string='External Link Name')
    external_link_url = fields.Char(string='External Link URL')

    residential_photo_id = fields.Many2many(comodel_name="ir.attachment",
                                            relation="m2m_ir_residential_rel",
                                            column1="m2m_id",
                                            column2="attachment_id",
                                            )
    residential_floor_plans_id = fields.Many2many(comodel_name="ir.attachment",
                                                  relation="m2m_ir_floor_plans_residential_rel",
                                                  column1="m2m_id",
                                                  column2="attachment_id",
                                                  )

    residential_documents_id = fields.Many2many(comodel_name="ir.attachment",
                                                relation="m2m_ir_residential_documents_rel",
                                                column1="m2m_id",
                                                column2="attachment_id",
                                                )
    listing_desc = fields.Boolean(string='Listing description and title information agree with what’s on the forms')
    listing_desc_id = fields.Many2many(comodel_name="ir.attachment",
                                                relation="m2m_ir_listing_desc_rel",
                                                column1="m2m_id",
                                                column2="attachment_id",)

    all_forms = fields.Boolean(string='All forms are signed by the owner / landlord')
    all_forms_id = fields.Many2many(comodel_name="ir.attachment",
                                       relation="m2m_ir_all_forms_rel",
                                       column1="m2m_id",
                                       column2="attachment_id", )

    matches = fields.Boolean(string='The price on any form matches that of the listing')
    matches_id = fields.Many2many(comodel_name="ir.attachment",
                                    relation="m2m_ir_matches_rel",
                                    column1="m2m_id",
                                    column2="attachment_id", )

    leasing_form = fields.Boolean(string='The property size on the Title deed matches the property size on the Sales/Leasing form')
    leasing_form_id = fields.Many2many(comodel_name="ir.attachment",
                                  relation="m2m_ir_leasing_form_rel",
                                  column1="m2m_id",
                                  column2="attachment_id", )

    nbps_copy = fields.Boolean(string='Copy of the owner’s / landlord’s Emirates ID / passport is signed by them')
    nbps_copy_id = fields.Many2many(comodel_name="ir.attachment",
                                       relation="m2m_ir_nbps_copy_rel",
                                       column1="m2m_id",
                                       column2="attachment_id", )

    ids_match = fields.Boolean(string='Signature on all forms and IDs match')
    ids_match_id = fields.Many2many(comodel_name="ir.attachment",
                                    relation="m2m_ir_ids_match_rel",
                                    column1="m2m_id",
                                    column2="attachment_id", )
    power_of_attorney = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'NO'),
    ] , default='no')
    power_of_attorney_id = fields.Many2many(comodel_name="ir.attachment",
                                    relation="m2m_ir_power_of_attorney_rel",
                                    column1="m2m_id",
                                    column2="attachment_id", )

    supporting_documents = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'NO'),
    ], default='no')
    supporting_documents_id = fields.Many2many(comodel_name="ir.attachment",
                                            relation="m2m_ir_supporting_documents_rel",
                                            column1="m2m_id",
                                            column2="attachment_id", )

    youtube_video_id = fields.Char(string='Youtube Video ID')
    virtual_tour_url = fields.Char(string='Virtual Tour URL')
    matter_port_id = fields.Char(string='Matter Port ID')

    reference_number = fields.Char('Reference Number')
    permit_number = fields.Char('Permit Number')
    offering_type = fields.Char('Offering Type')
    city = fields.Char('City')
    community = fields.Char('Community')
    property_name = fields.Char('Property Name')
    title_en = fields.Char('Title')
    description_en = fields.Text('Description')
    size = fields.Integer('Size')
    bedroom = fields.Integer('Bedroom')
    bathroom = fields.Integer('Bathroom')

    parking = fields.Integer('Parking')
    furnished = fields.Boolean('Furnished')
    sub_community = fields.Char('Sub Community')
    private_amenities = fields.Char('Private Amenities')
    thumbnail_image = fields.Binary('Thumbnail Image')


    image1 = fields.Image('Image 1')
    image2 = fields.Image('Image 2')
    image3 = fields.Image('Image 3')
    image4 = fields.Image('Image 4')
    image5 = fields.Image('Image 5')
    image6 = fields.Image('Image 6')
    image7 = fields.Image('Image 7')
    image8 = fields.Image('Image 8')
    image9 = fields.Image('Image 9')
    image10 = fields.Image('Image 10')

    state = fields.Selection(
        [('new', 'New'), ('available_for_sale', 'Avaialable For Sale'), ('available_for_rent', 'Avaialable For Rent'),
         ('published', 'Published'), ('booked', 'Booked'), ('rented', 'Rented'), ('sold', 'Sold'),
         ('cancel', 'Cancelled')],
        default='new')

    def action_submit(self):
        if self.listing_type == 'for_sale':
            self.state = 'available_for_sale'
        else:
            self.state = 'available_for_rent'

    def action_publish(self):
        self.state = 'published'

    def action_book(self):
        self.state = 'booked'

    def action_sold(self):
        self.state = 'sold'

    def action_rent(self):
        self.state = 'rented'

    def action_cancel(self):
        self.state = 'cancel'

    @api.model
    def year_selection(self):
        year = 2000  # replace 2000 with your a start year
        year_list = []
        while year != 2050:  # replace 2030 with your end year
            year_list.append((str(year), str(year)))
            year += 1
        return year_list


from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CRMLeadFields(models.Model):
    _inherit = 'crm.lead'

    country_id = fields.Many2one('res.country', string="Country")
    nationality_id = fields.Many2one('res.country', string="Nationality")
    area = fields.Many2one('area.details', string="Area")

    property_type_id = fields.Many2one('property.type', string="Property Type")
    transaction_type = fields.Selection([
        ('sale', 'Sale'),
        ('rent', 'Rent'),
    ])

    no_of_bedrooms = fields.Selection(selection=[(f'a{i}', i) for i in range(1, 21)], string='No of Bedrooms')
    no_of_bathrooms = fields.Selection(selection=[(f'a{i}', i) for i in range(1, 21)], string='No of Bathrooms')

    size_in_sqft = fields.Float(string='Size In Sqft')
    size_in_sqm = fields.Float(string='Size In Sqm', force_save="1")
    no_of_parkings = fields.Integer(string='No. of Parkings')
    budget_from = fields.Integer(string='Budget From')
    budget_to = fields.Integer(string='Budget To')
    button_show = fields.Boolean(default=False)

    crm_media_id = fields.Many2many(comodel_name="ir.attachment",
                                    relation="m2m_ir_crm_media_rel",
                                    column1="m2m_id",
                                    column2="attachment_id",
                                    )

    @api.onchange('size_in_sqft')
    def set_value_sqft(self):
        self.size_in_sqm = self.size_in_sqft * 0.092903

    @api.onchange('size_in_sqm')
    def set_value_sq(self):
        self.size_in_sqft = self.size_in_sqm / 0.092903

    def write(self, create_vals):
        res = super(CRMLeadFields, self).write(create_vals)
        act_type_xmlid = 'mail.mail_activity_data_todo'
        summary = 'Notification'
        note = 'Notofication: ' + self.name + ' will be unreserved Automatically.'
        if act_type_xmlid:
            activity_type = self.sudo().env.ref(act_type_xmlid)
        model_id = self.env['ir.model']._get(self._name).id
        vals = {
            'activity_type_id': activity_type.id,
            'summary': summary or activity_type.summary,
            'automated': True,
            'note': note,
            'res_model_id': model_id,
            'res_id': self.id,
            'user_id': self.user_id.id,
        }
        # if self.user_id in vals:
        #     # print(self.user_id.name)
        activities = self.env['mail.activity'].create(vals)
        return res

    def action_set_won_rainbowman(self):
        vals = super(CRMLeadFields, self).action_set_won_rainbowman()
        self.button_show = True
        return vals

    def notify_action(self):
        template_id = self.env.ref('property.email_template').id
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(self.id, force_send=True)

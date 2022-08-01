# -*- coding: utf-8 -*-
{
    'name': "property",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base' , 'crm' , 'resource' , 'mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/branch.xml',
        'views/users_field.xml',
        'views/commercial_property.xml',
        'views/property_type.xml',
        'views/residential_property.xml',
        'views/mandate_details.xml',
        'views/tenancy_contract.xml',
        'views/cm_lead.xml',
        'views/res_partner_field.xml',
        'views/area_details.xml',
        'views/feature_amenities.xml',
        'report/report.xml',
        'report/tenancy_contract.xml',
        'report/acknowledgement_report.xml',
        'report/addendum_report.xml',
        'report/commercial_property_report.xml',
        'report/residential_property_report.xml',
        'data/mail_template.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}

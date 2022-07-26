# -*- coding: utf-8 -*-
{
    'name': "SRS Overall",

    'summary': """
        SRS Customization""",

    'description': """
        SRS Customization
    """,

    'author': "Viltco",
    'website': "http://www.viltco.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'property',
    'version': '14.0.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'property_rental_mgt_app', 'timer'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/property_views.xml',
        'views/assets.xml',
    ],

}

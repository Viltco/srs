# -*- coding: utf-8 -*-
{
    'name': "PDC Payments",

    'summary': """
        PDC Payments Cheque Print""",

    'description': """
        PDC Payments Cheque Print
    """,

    'author': "Viltco",
    'website': "http://www.viltco.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '14.0.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/pdc_sequence.xml',
        'security/security.xml',
        'reports/pdc_payment_report.xml',
        'reports/pdc_payment_template.xml',
        'wizards/pdc_payment_wizard_views.xml',
        'views/pdc_payment_views.xml',
    ],

}

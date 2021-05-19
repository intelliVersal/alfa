# -*- coding: utf-8 -*-
{
    'name': "Customization for Expenses under payment",
    'summary': """Custom module for expense payment""",
    'author': "SIT & think digital",
    'website': "http://sitco.odoo.com/",
    'category': 'Custom',
    'version': '12.0.1',

    'depends': ['base','mail','hr','saudi_hr_employee','account'],

    'data': [
        'data/ir_sequence.xml',
        'security/ir.model.access.csv',
        'views/expense_payment_report.xml',
        'views/expense_payment_view.xml'
            ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}

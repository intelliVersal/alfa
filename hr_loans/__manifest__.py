# -*- coding: utf-8 -*-
{
    'name': "Hr Loans", # Faisal for test
    'summary': ' Hr Loans',
    'description': " Hr Loans ",
    'author': "OserGroup",
    'website': "",
    'category': 'Saudi HR',
    'version': '0.1',
    'depends': [
        'mail',
        'basic_hr',
        'base',
        'saudi_hr_employee',
        'saudi_hr_contract',
        'saudi_hr_payroll',
        # 'saudi_hr_leaves',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/hr_loans.xml',
        'views/hr_rewards.xml',
        'views/request_sequence.xml',
        'views/salary_structure_data.xml',
        'wizard/multi_approval.xml',
        'res_config_view.xml',
    ],
}

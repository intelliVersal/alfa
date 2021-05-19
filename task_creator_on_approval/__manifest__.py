# -*- coding: utf-8 -*-
{
    'name': "Task Creation On Approval from the Management",
    'summary': """Custom module for the creation of task on approval by the management and assigned to the respective department authority,
    from this module task will assign to the users automatically, task is related to the payment, subscription ren""",
    'author': "SIT & think digital",
    'website': "http://sitco.odoo.com/",
    'category': 'Custom',
    'version': '12.0.1',

    'depends': ['base','hr','account','sale_subscription','project','custom_payment'],

    'data': [
        'security/security.xml',
        'data/data.xml',
        'views/cron_view.xml',
        'views/model_view.xml',
            ],

    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}

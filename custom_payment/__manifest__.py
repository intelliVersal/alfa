# -*- coding: utf-8 -*-

{
    'name': "Customization for payments",
    'summary': " ",
    'sequence': 0,
    'description': " ",
    'author': "SIT and think digital",
    'website': "",
    'category': 'custom',
    'version': '0.1',
    'depends': [
        'base','hr',
        'account','payment'
    ],
    'data': ['security/security.xml',
        'views/base_accounting.xml',
    ],
	'application': True,
    'installable': True,
    'auto_install': False,
}

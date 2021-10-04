# -*- coding: utf-8 -*-
{
    'name': "Custom module for all requirement specifically for Alfa door.",
    'summary': """Mixed customization.""",
    'author': "SIT & Think Digital",
    'website': "https://www.linkedin.com/in/engr-muhammad-faizan-80011782/",
    'category': 'Custom',
    'version': '12.0.1',

    'depends': ['sale','stock','sale_stock'],

    'data': [
        'views/model_view.xml',
        'views/sale_order_template.xml',
        'views/manufacturing_template.xml'
            ],

    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}


{
    'name': 'Custom Product Labels',
    'version': '12.0.1.0.4',
    'category': 'Extra Tools',
    'author': 'SIT & Think Digital',
    'website': "sitco.odoo.com",
    'license': 'LGPL-3',
    'summary': """Print custom product labels with barcode""",
    'images': ['static/description/banner.png'],
    'description': """
Module allows to print custom product barcode labels and tags on different paper formats.
This module include the one label template with size: 57x35mm, paperformat: A4 (21 pcs per sheet, 3 pcs x 7 rows).
It is possible to add additional label templates with our other modules.
    """,
    'depends': ['product'],
    'data': [
        'wizard/print_product_label_views.xml',
        'report/product_label_templates.xml',
        'report/product_label_reports.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}

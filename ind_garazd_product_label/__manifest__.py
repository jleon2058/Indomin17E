{
    'name': 'Indomin - Custom Product Labels',
    'version': '17.0.1.0.0',
    'category': 'Extra Tools',
    'author': 'Dany Chavez',
    'license': 'LGPL-3',
    'depends': [
        'garazd_product_label',
        'stock',
        'account'
    ],
    'data': [
        'wizards/print_product_label_views.xml',
        'templates/product_label_templates.xml',
        'templates/print_label_reports.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

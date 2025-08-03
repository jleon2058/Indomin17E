{
    'name': 'ind_account',
    'summary': 'Modificaciones en account',
    'version': '17.0.1.0.3',
    'author': 'Juan Carlos León Huayta',
    'maintainer': 'Dany Chavez',
    'depends': [
        'account',
        'stock_account',
        'purchase_stock'
    ],
    'data': [
        'views/account_move.xml',
        'views/account_move_line.xml',
        'reports/ir_actions_report_template.xml',
        'reports/ir_actions_report.xml',
        'views/account_payment.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}

{
    'name': 'Indomin - Campos adicionales compatible con CONCAR',
    'version': '17.0.1.0.2',
    'author': 'Juan Carlos León Huayta',
    'maintainer': 'Ronaldo Lopez',
    'category': 'Extra tools',
    'depends': [
        'base',
        'account'
    ],
    'data': [
        'views/account_move_views.xml',
        'views/account_payment_views.xml',
        'views/account_move_line_views.xml',
        "wizards/account_move_line_export_wizard_views.xml",
        "security/ir.model.access.csv",
        "views/account_analytic_account.xml"
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',
}

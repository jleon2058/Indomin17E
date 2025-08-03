{
    'name': 'Analytic Partner History',
    'version': '17.0.2.0.3',
    'summary': 'Historial de clientes asignados a centros de costo',
    'author': 'Dany Chavez',
    'category': 'Accounting',
    'depends': [
        'account_accountant'
    ],
    'data': [
        'security/analytic_partner_history_security.xml',
        'security/ir.model.access.csv',
        'views/account_menus.xml',
        'views/analytic_location_views.xml',
        'views/account_analytic_account_partner_history_views.xml',
        'views/account_analytic_account_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}

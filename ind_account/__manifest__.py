{
    'name': 'ind_account',
    'version': '17.0.1.0.1',

    'depends': ['account','stock_account'],
    'data': [
        'views/account_move.xml',  # Asegurar que el XML se cargue
    ],
    'installable': True,
    'application': False,
}
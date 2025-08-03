{
    'name': 'Indomin Employee Contracts',
    "author": "Javier Yataco",
    "version": "17.0.1.0.1",
    'category': 'Human Resources/Contracts',
    'sequence': 335,
    'description': """
Se agrega los contratos, tipos de adendas para empleados
de Indomin.
    """,
    'website': 'www.indomin.net',
    'depends': ['hr','hr_contract'],
    'data': [
        'report/hr_contract_addendum.xml',
        'report/hr_first_contract.xml',
        'report/hr_contract_addendum_daily.xml',
    ],
    'assets': {
        'web.report_assets_common': [
            'ind_hr_contract/static/src/scss/styles.scss',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'AGPL-3',
}

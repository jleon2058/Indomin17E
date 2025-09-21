{
    'name': 'Checklist de Documentos para Empleados',
    'version': '17.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Sistema de checklist de documentos para empleados',
    'description': """
        Permite gestionar checklist de documentos requeridos para empleados
        que ingresan a elaborar
    """,
    'author': 'Juan Leon',
    'website': 'https://www.indomin.net',
    'depends': ['hr'],
    'data': [
        'views/hr_employee_views.xml',
    ],
    # 'assets': {
    #     'web.assets_backend': [
    #         'ind_hr_checklist/static/src/xml/hr_checklist_templates.xml',
    #         'ind_hr_checklist/static/src/js/progress_bar.js',
    #     ],
    # },
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
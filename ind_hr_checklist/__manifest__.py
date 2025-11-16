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
    'depends': ['base','hr'],
    "data": [
        "data/hr_employee_actions.xml",
        "security/hr_checklist_security.xml",
        "security/ir.model.access.csv",
        "views/hr_employee_views.xml",
        "views/res_config_settings_views.xml",
        "wizards/register_audit_checklist_wizard.xml"
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
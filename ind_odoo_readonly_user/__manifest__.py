{
    'name': "Mejoras Readonly User Access",
    'version': '17.0.1.0.0',
    'category': 'Extra Tools',
    'autor': 'Juan Leon',
    'summary': "Habilitación de acceso a los reportes generados de algunas vistas",
    'description': """
        Extension del módulo odoo_readonly_user para permitir la obtención de reportes
    """,
    'website': 'https://www.tuempresa.com',
    'depends': ['odoo_readonly_user'],
    'data': [],
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
    'application': False,
    # Forzar que se ejecute después del módulo original
    'sequence': 100,
}
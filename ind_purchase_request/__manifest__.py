{
    'name': 'Indomin - Solicitud de Compra',
    'author': 'Dany Chavez',
    'version': '17.0.1.1.8',
    'summary': 'Cambios aplicados para el módulo Purchase Request',
    'category': 'Purchase Management',
    'depends': [
        'analytic_partner_history',
        'purchase_request',
        'report_xlsx',
        'hr',
        'purchase_stock',
        'account',
        'analytic',
        'base'
    ],
    'data': [
        'reports/ir_actions_report_templates.xml',
        'reports/ir_actions_report.xml',
        'wizards/purchase_request_line_make_purchase_order.xml',
        'wizards/purchase_request_import_line.xml',
        'views/purchase_order_line_views.xml',
        'views/purchase_order_views.xml',
        'views/purchase_request_line_views.xml',
        'views/purchase_request_views.xml',
        'security/purchase_request_security.xml',
        'security/purchase_order_security.xml',
        'security/ir.model.access.csv'
    ],
    'assets': {
        'web.assets_backend': [
            'ind_purchase_request/static/src/overrides/**/*',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}

{
    'name': 'Indomin - Orden de Compra',
    'author': 'Dany Chavez',
    'version': '17.0.1.0.3',
    'summary': 'Cambios aplicados para el módulo Purchase Order',
    'category': 'Purchase Management',
    'depends': [
        'report_xlsx',
        'purchase',
        'ind_purchase_request',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizards/report_purchase_order_views.xml',
        'wizards/report_volume_approved_views.xml',
        'wizards/report_rfq_approved_views.xml',
        'views/purchase_menus.xml',
        'reports/ir_actions_report.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}

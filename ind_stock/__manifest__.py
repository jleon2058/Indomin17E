{
    'name':'Indomin Stock',
    'author':'Juan Carlos León',
    'maintainer': 'Dany Chavez',
    'version': '17.0.1.0.1',
    'summary': 'Cambios aplicados para el módulo Inventario ',
    'category': 'Inventory/Inventory',
    'depends':[
        'sale_stock',
        'report_xlsx',
        'purchase_request',
        'hr',
        'stock_analytic',
        'dv_stock_picking_employee_pin',
        'ind_kardex_valorado_general'
    ],
    'data':[
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'views/stock_picking_views.xml',
        'reports/ir_actions_report_templates.xml',
        'reports/ir_actions_report.xml'
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3'
}

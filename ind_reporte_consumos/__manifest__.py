{
    'name': 'Indomin - Reporte Consumos',
    'author': 'Dany Chavez',
    'version': '17.0.2.0.0',
    'description': 'Reporte de consumos a nivel del almacen',
    'depends': [
        "base",
        "stock",
        "purchase_request",
        "account",
        "product",
        "stock_analytic"
    ],
    'data':[
        "security/access_groups.xml",
        "security/ir.model.access.csv",
        "wizards/consumption_analysis_wizard_views.xml"
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}

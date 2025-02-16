{
    "name": "Indomin Purchase Request",
    "author": "Javier Yataco",
    'version': "17.0.1.1.0",
    'depends': ['purchase', 'stock','purchase_request'],
    'category': 'Purchases',
    'summary': 'Transferir la distribución analítica de las líneas de pedido a los movimientos de inventario.',
    'description': """
        Al confirmar un pedido de compra, transfiere el valor de analytic_distribution
        desde las líneas de pedido de compra a los movimientos de inventario generados.
    """,
    'data':[
        'security/res_group.xml',
        'security/purchase_request_security.xml',
        'security/purchase_order_security.xml',
        'security/ir.model.access.xml',
        'reports/report_purchase_request.xml',
        'reports/purchase_order_report.xml',
        'views/purchase_request_report.xml',
        'views/purchase_order.xml',
        'views/purchase_request.xml',
        'views/purchase_request_line.xml'
    ],
    'installable': True,
    'application': False,
}
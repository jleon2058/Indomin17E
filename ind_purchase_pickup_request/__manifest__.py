{
    'name': "Purchase Pickup Request",
    'version': '17.0.1.0.1',
    'category': 'Purchases',
    'summary': 'Add pickup request creation from purchase orders',
    'description': """
        This module allows users to create pickup requests directly from purchase orders.
        Pickup requests are then viewable in the Purchases reports section.
    """,
    'depends': [
        'base',
        'ind_stock',
        'ind_purchase_request'
    ],
    'data': [
        'security/access_groups.xml',
        'security/ir.model.access.csv',
        'security/purchase_pickup_request.xml',
        'views/pickup_request_views.xml',
        'views/purchase_order_views.xml',
        'views/pickup_driver_views.xml',
        'reports/ir_actions_report.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}

{
    'name': "product_cost_invoice",
    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    'description': """
        Long description of module's purpose
    """,
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '17.0.1.0.1',
    'depends': ['base', 'purchase_stock', 'account','stock_account'],
    'data': [
        'views/views.xml',
        'views/templates.xml',
        'views/stock_valuation_layer.xml'
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'license': 'LGPL-3',
}
